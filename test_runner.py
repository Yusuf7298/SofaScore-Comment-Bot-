import json
import logging
import sys
import copy
import time
import re
import random
from core.scheduler import Scheduler
from core.navigation import Navigator
from core.session_manager import SessionManager
from selenium.common.exceptions import WebDriverException
from utils.helpers import logger

class ValidationRunner:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r') as f:
            self.base_config = json.load(f)
            
        self.config = copy.deepcopy(self.base_config)
        
        if "bot" not in self.config:
            self.config["bot"] = {}
            
        self.config["bot"]["dry_run"] = True 
        self.config["bot"]["max_comments_per_match"] = 5 
        
        if "anti_ban" not in self.config:
            self.config["anti_ban"] = {}
            
        self.config["anti_ban"]["skip_chance_percent"] = 0
        self.config["anti_ban"]["account_switch_delay_seconds"] = 1
        self.config["bot"]["cooldown_between_comments_seconds"] = 1
            
        self.metrics = {
            "total_runs": 0,
            "successes": 0,
            "failures": 0,
            "error_types": {},
            "action_times": [],
            "total_fallbacks": 0,
            "primary_selector_hits": 0,
            "total_queries": 0,
            "slow_actions": 0,
            "cycle_times": [],
            "skipped_actions": 0,
            "recovery_triggers": 0,
            "session_restarts": 0,
            "slow_action_details": [],
            "root_causes": {
                "fallback_overuse": 0,
                "element_not_visible": 0,
                "recovery_triggered": 0,
                "forced_failures": 0
            }
        }
        
    def _stress_monkey_patch(self):
        """Final Audit: Injection of real-world latency and failure handling verification."""
        original_fast_poll = Navigator._fast_poll_elements
        
        def stressed_poll(nav_self, optimized_list, require_interactable=False, global_timeout=5.0):
            time.sleep(random.uniform(0.1, 0.4))
            
            r = random.random()
            if r < 0.05:
                return None, None, 5.0, len(optimized_list)
            elif r < 0.08:
                raise WebDriverException("Stressed Driver Shutdown")
                
            return original_fast_poll(nav_self, optimized_list, require_interactable, global_timeout)

        Navigator._fast_poll_elements = stressed_poll
        
    def _configure_logging(self):
        file_handler = logging.FileHandler("validation_runner.log")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        class MetricsHandler(logging.Handler):
            def __init__(self, metrics):
                super().__init__()
                self.metrics = metrics
                
            def emit(self, record):
                msg = self.format(record)
                msg_lower = msg.lower()
                
                if "element not found, skipping" in msg_lower:
                    self.metrics["skipped_actions"] += 1
                    self.metrics["root_causes"]["element_not_visible"] += 1
                elif "recovery triggered" in msg_lower:
                    self.metrics["recovery_triggers"] += 1
                    self.metrics["root_causes"]["recovery_triggered"] += 1
                elif "comment posted successfully" in msg_lower or "comment simulated successfully" in msg_lower:
                    self.metrics["successes"] += 1
                elif "[metric]" in msg_lower:
                    try:
                        match = re.search(r"found in ([\d\.]+)s.*fallbacks: (\d+)", msg_lower)
                        if match:
                            res_time = float(match.group(1))
                            fallbacks = int(match.group(2))
                            
                            self.metrics["action_times"].append(res_time)
                            self.metrics["total_fallbacks"] += fallbacks
                            self.metrics["total_queries"] += 1
                            if fallbacks == 0: self.metrics["primary_selector_hits"] += 1
                            
                            if res_time > 5.0:
                                self.metrics["slow_actions"] += 1
                                cause = "fallback_overuse" if fallbacks > 1 else "element_not_visible"
                                if "recovery" in msg_lower: cause = "recovery_triggered"
                                self.metrics["slow_action_details"].append(f"Action ({res_time:.2s}s) - Cause: {cause}")
                    except Exception: pass
                
                if record.levelno >= logging.ERROR:
                    self.metrics["failures"] += 1
                    
        self.metrics_handler = MetricsHandler(self.metrics)
        logger.addHandler(self.metrics_handler)
        
    def run(self):
        self._configure_logging()
        self._stress_monkey_patch()
        logger.info("=== STARTING FINAL ARCHITECTURAL AUDIT ===")
        
        expected_cycles = 6
        
        for i in range(expected_cycles):
            logger.info(f"--- VALIDATION CYCLE {i+1}/{expected_cycles} ---")
            
            if i == 1:
                self.metrics["action_times"] = []
                self.metrics["total_fallbacks"] = 0
                self.metrics["total_queries"] = 0
                self.metrics["primary_selector_hits"] = 0
                self.metrics["slow_actions"] = 0
                self.metrics["skipped_actions"] = 0
                self.metrics["recovery_triggers"] = 0
                self.metrics["failures"] = 0
            
            scheduler = Scheduler(self.config)
            cycle_start = time.time()
            try:
                scheduler.run_sequential()
            except Exception as e:
                logger.error(f"Cycle Failure: {e}")
            cycle_duration = time.time() - cycle_start
            
            if i > 0:
                self.metrics["cycle_times"].append(cycle_duration)
                self.metrics["total_runs"] += 1
                
        self.print_summary()
        
    def print_summary(self):
        logger.removeHandler(self.metrics_handler)
        
        print("\n=== PERFORMANCE REPORT ===\n")
        
        action_times = sorted(self.metrics["action_times"])
        if action_times:
            p95 = action_times[int(len(action_times) * 0.95)]
            avg = sum(action_times) / len(action_times)
            min_t = action_times[0]
            max_t = action_times[-1]
            efficiency = (self.metrics["primary_selector_hits"] / self.metrics["total_queries"]) * 100.0 if self.metrics["total_queries"] > 0 else 0.0
            avg_fallbacks = self.metrics["total_fallbacks"] / self.metrics["total_queries"] if self.metrics["total_queries"] > 0 else 0.0
        else:
            p95 = avg = min_t = max_t = efficiency = avg_fallbacks = 0.0

        print(f"Latency:")
        print(f"- Min: {min_t:.2f}s")
        print(f"- Avg: {avg:.2f}s")
        print(f"- Max: {max_t:.2f}s")
        print(f"- P95: {p95:.2f}s")
        
        print(f"\nSelectors:")
        print(f"- Efficiency: {efficiency:.1f}%")
        print(f"- Avg Fallbacks: {avg_fallbacks:.2f}")
        
        print(f"\nStability:")
        print(f"- Skipped Actions: {self.metrics['skipped_actions']}")
        print(f"- Recovery Triggered: {self.metrics['recovery_triggers']}")
        print(f"- Failures: {self.metrics['failures']}")
        
        print(f"\nDiagnostics:")
        if self.metrics["slow_action_details"]:
            for detail in self.metrics["slow_action_details"]:
                print(f"- {detail}")
        else:
            print("- None (All actions under 5s)")

        score = 100.0
        score -= (self.metrics["slow_actions"] * 5)
        
        slow_cycles = sum(1 for t in self.metrics["cycle_times"] if t > 30.0)
        score -= (slow_cycles * 10)
        
        if avg_fallbacks > 2: score -= 10
        if efficiency < 70.0: score -= 10
        if self.metrics["failures"] > 0 or self.metrics["skipped_actions"] > 1: score -= 15
        
        score = max(0.0, score)
        print(f"\nScore:")
        print(f"- Optimization Score: {score:.1f}/100")
        
        print(f"\nFinal Verdict:")
        if score >= 90.0:
            print("PRODUCTION READY")
        else:
            print("NEEDS OPTIMIZATION")
        print("\n" + "="*50)

if __name__ == "__main__":
    runner = ValidationRunner()
    runner.run()
