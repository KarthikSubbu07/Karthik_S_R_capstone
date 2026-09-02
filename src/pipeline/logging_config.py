import json, logging, time
from pathlib import Path

class JsonFormatter(logging.Formatter):
    """Emit one JSON record per log line — machine-readable, grep-friendly."""
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "ts": round(time.time(), 3),
                "level": record.levelname,
                "msg": record.getMessage,
                "logger": record.name 
            }
        )

    def get_logger(name="pipeline", log_path="logs/pipeline.log") -> logging.Logger:
        """function that returns a configured `logging.Logger`"""
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)

        if log.handlers:
            return log

        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(JsonFormatter())
        log.addhandler(fh)
        return log
