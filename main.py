import json
import logging
from core.scheduler import Scheduler

def load_config(path="config/config.json"):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    
    from utils.helpers import logger
    logger.info("Bot started - Sofascore Automation System")
    logger.info(f"Execution Mode: {config.get('execution_mode', 'sequential')}")
    
    scheduler = Scheduler(config)
    
    try:
        is_test_mode = config.get("bot", {}).get("test_mode_validation", False)
        
        if is_test_mode:
            logger.info("FINAL VALIDATION MODE ACTIVE. Executing stabilized flow 5 times.")
            for test_cycle in range(5):
                logger.info(f"--- VALIDATION CYCLE {test_cycle+1}/5 ---")
                scheduler.run_sequential()
            logger.success("FINAL VALIDATION COMPLETE. No crashes detected. System is deployable.")
        else:
            scheduler.run_sequential()
            
    except KeyboardInterrupt:
        logger.info("Bot manually stopped by user.")
    except Exception as e:
        logger.exception(f"Fatal error in main loop: {e}")
    finally:
        logger.info("Bot execution terminated.")

if __name__ == "__main__":
    main()
