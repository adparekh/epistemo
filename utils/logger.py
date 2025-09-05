"""
Streamlit-compatible logging utility.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum

class LogLevel(Enum):
    """Log levels for the Streamlit logger."""
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

class StreamlitLogger:
    """Logger that integrates with Streamlit interface."""
    
    def __init__(self, max_logs: int = 100):
        self.max_logs = max_logs
        if "logs" not in st.session_state:
            st.session_state.logs = []
    
    @property
    def logs(self) -> List[Dict[str, Any]]:
        """Get current logs from session state."""
        return st.session_state.get("logs", [])
    
    def _add_log(self, level: LogLevel, message: str):
        """Add a log entry."""
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level.value,
            "message": message,
            "full_timestamp": datetime.now()
        }
        
        # Add to session state logs
        if "logs" not in st.session_state:
            st.session_state.logs = []
        
        st.session_state.logs.append(log_entry)
        # st.session_state.logs = st.session_state.logs  # triggers state update
        # st.experimental_rerun()  # force UI refresh]
        
        # Keep only the most recent logs
        if len(st.session_state.logs) > self.max_logs:
            st.session_state.logs = st.session_state.logs[-self.max_logs:]
    
    def info(self, message: str):
        """Log an info message."""
        self._add_log(LogLevel.INFO, message)
        print(f"ℹ️ {message}")
    
    def success(self, message: str):
        """Log a success message."""
        self._add_log(LogLevel.SUCCESS, message)
        print(f"✅ {message}")
    
    def warning(self, message: str):
        """Log a warning message."""
        self._add_log(LogLevel.WARNING, message)
        print(f"⚠️ {message}")
    
    def error(self, message: str):
        """Log an error message."""
        self._add_log(LogLevel.ERROR, message)
        print(f"❌ {message}")
    
    def clear_logs(self):
        """Clear all logs."""
        st.session_state.logs = []
    
    def render_logs(self):
        """Render the logs in the Streamlit interface."""
        # Log container with scrolling
        log_container = st.container()
        
        with log_container:
            if not self.logs:
                st.write("Thats in the beginning")
                st.info("No logs yet. Start a research query to see activity.")
                return
            

            st.write("You should be here now")
            # Show recent logs (latest first)
            recent_logs = list(reversed(self.logs[-20:]))  # Show last 20 logs
            
            for log in recent_logs:
                level = log["level"]
                message = log["message"]
                timestamp = log["timestamp"]
                
                # Choose appropriate Streamlit component based on log level
                if level == LogLevel.ERROR.value:
                    st.error(f"[{timestamp}] {message}")
                elif level == LogLevel.WARNING.value:
                    st.warning(f"[{timestamp}] {message}")
                elif level == LogLevel.SUCCESS.value:
                    st.success(f"[{timestamp}] {message}")
                else:  # INFO
                    st.info(f"[{timestamp}] {message}")