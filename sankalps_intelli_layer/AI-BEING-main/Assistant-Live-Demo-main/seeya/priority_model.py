import json
import os
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Any
import sqlite3
import os

class Prioritizer:
    """
    Email prioritization system using reinforcement learning.
    Learns from user feedback to improve email priority scoring.
    """
    
    def __init__(self, q_table_file='q_table.json', reward_history_file='reward_history.json'):
        self.q_table_file = q_table_file
        self.reward_history_file = reward_history_file
        self.q_table = self._load_q_table()
        self.reward_history = self._load_reward_history()
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.1
        
    def _load_q_table(self) -> Dict:
        """Load Q-table from file or initialize empty one."""
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def _save_q_table(self):
        """Save Q-table to file."""
        try:
            with open(self.q_table_file, 'w') as f:
                json.dump(self.q_table, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Q-table: {e}")
    
    def _load_reward_history(self) -> List:
        """Load reward history from file."""
        if os.path.exists(self.reward_history_file):
            try:
                with open(self.reward_history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def _save_reward_history(self):
        """Save reward history to file."""
        try:
            with open(self.reward_history_file, 'w') as f:
                json.dump(self.reward_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save reward history: {e}")
    
    def _extract_features(self, email: Dict) -> str:
        """Extract features from email for Q-table state representation."""
        features = []
        
        # Tag-based features
        tag = email.get('tag', 'GENERAL')
        features.append(f"tag_{tag}")
        
        # Confidence level
        confidence = email.get('tag_confidence', 0)
        if confidence > 0.7:
            features.append("high_confidence")
        elif confidence > 0.4:
            features.append("medium_confidence")
        else:
            features.append("low_confidence")
        
        # Sentiment
        sentiment = email.get('sentiment_score', 0)
        if sentiment > 0.1:
            features.append("positive_sentiment")
        elif sentiment < -0.1:
            features.append("negative_sentiment")
        else:
            features.append("neutral_sentiment")
        
        # Metrics-based features
        metrics = email.get('metrics', {})
        urgency = metrics.get('urgency', 'low')
        features.append(f"urgency_{urgency}")
        
        if metrics.get('has_deadline', False):
            features.append("has_deadline")
        
        intent = metrics.get('intent', 'general')
        features.append(f"intent_{intent}")
        
        # Create state key
        return "_".join(sorted(features))
    
    def _calculate_base_score(self, email: Dict) -> float:
        """Calculate base priority score using heuristics."""
        score = 0.0
        
        # Tag-based scoring
        tag_scores = {
            'URGENT': 10.0,
            'SECURITY': 9.0,
            'MEETING': 8.0,
            'FINANCIAL': 7.0,
            'IMPORTANT': 6.0,
            'GENERAL': 3.0,
            'PROMOTIONAL': 2.0,
            'NEWSLETTER': 1.0
        }
        
        tag = email.get('tag', 'GENERAL')
        score += tag_scores.get(tag, 3.0)
        
        # Confidence boost
        confidence = email.get('tag_confidence', 0)
        score += confidence * 2.0
        
        # Sentiment adjustment
        sentiment = email.get('sentiment_score', 0)
        if sentiment < -0.3:  # Very negative sentiment
            score += 2.0
        elif sentiment < -0.1:  # Negative sentiment
            score += 1.0
        
        # Metrics-based adjustments
        metrics = email.get('metrics', {})
        
        urgency_scores = {'high': 3.0, 'medium': 1.5, 'low': 0.0}
        urgency = metrics.get('urgency', 'low')
        score += urgency_scores.get(urgency, 0.0)
        
        if metrics.get('has_deadline', False):
            score += 2.0
        
        # Intent-based scoring
        intent_scores = {
            'request': 2.0,
            'question': 1.5,
            'complaint': 2.5,
            'urgent': 3.0,
            'meeting': 2.0,
            'general': 0.0
        }
        intent = metrics.get('intent', 'general')
        score += intent_scores.get(intent, 0.0)
        
        return max(score, 0.1)  # Ensure minimum score
    
    def prioritize_emails(self, emails: List[Dict]) -> List[Tuple[float, Dict]]:
        """
        Prioritize emails using reinforcement learning enhanced scoring.
        Returns list of (score, email) tuples sorted by priority.
        """
        scored_emails = []
        
        for email in emails:
            # Calculate base score
            base_score = self._calculate_base_score(email)
            
            # Get Q-learning adjustment
            state = self._extract_features(email)
            q_adjustment = self.q_table.get(state, 0.0)
            
            # Combine scores
            final_score = base_score + q_adjustment
            
            scored_emails.append((final_score, email))
        
        # Sort by score (descending)
        scored_emails.sort(key=lambda x: x[0], reverse=True)
        
        return scored_emails
    
    def update(self, email: Dict, user_feedback: float):
        """
        Update Q-table based on user feedback.
        
        Args:
            email: Email that was prioritized
            user_feedback: Feedback score (-1 to 1, where 1 is perfect priority)
        """
        state = self._extract_features(email)
        current_q = self.q_table.get(state, 0.0)
        
        # Q-learning update
        reward = user_feedback
        new_q = current_q + self.learning_rate * (reward - current_q)
        
        self.q_table[state] = new_q
        
        # Record reward
        self.reward_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'reward': reward,
            'old_q': current_q,
            'new_q': new_q
        })
        
        # Save updates
        self._save_q_table()
        self._save_reward_history()
    
    def update_from_feedback_table(self, db_path: str = None):
        """
        Dynamically update learning from Nilesh's unified DB feedback table.
        Applies EMA of recent feedback to a GLOBAL state and common tag states.
        """
        try:
            if not db_path:
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nilesh', 'data', 'assistant_core.db'))
            if not os.path.exists(db_path):
                return
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT feedback_value FROM feedback ORDER BY id DESC LIMIT 200")
            rows = cur.fetchall()
        except Exception:
            return
        finally:
            try:
                conn.close()
            except Exception:
                pass
        if not rows:
            return
        values = [float(r["feedback_value"]) for r in rows if r["feedback_value"] is not None]
        if not values:
            return
        ema = 0.0
        alpha = 0.2
        for v in values:
            ema = alpha * v + (1 - alpha) * ema
        current_q = self.q_table.get("GLOBAL", 0.0)
        new_q = current_q + self.learning_rate * (ema - current_q)
        self.q_table["GLOBAL"] = new_q
        self.reward_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': 'GLOBAL',
            'reward': ema,
            'old_q': current_q,
            'new_q': new_q
        })
        self._save_q_table()
        self._save_reward_history()
    
    def decay_exploration(self, min_rate: float = 0.01, decay: float = 0.995):
        """Gradually decay exploration rate to stabilize learning."""
        self.exploration_rate = max(min_rate, self.exploration_rate * decay)
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics."""
        stats = {
            'total_states': len(self.q_table),
            'total_feedback': len(self.reward_history),
            'total_episodes': len(self.reward_history),
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor
        }
        
        if self.reward_history:
            recent_rewards = [r['reward'] for r in self.reward_history[-100:]]
            stats.update({
                'avg_reward': np.mean(recent_rewards),
                'recent_performance': [r['reward'] for r in self.reward_history[-10:]],
                'reward_trend': 'improving' if len(recent_rewards) > 10 and 
                               np.mean(recent_rewards[-10:]) > np.mean(recent_rewards[-20:-10]) 
                               else 'stable'
            })
            
            # Q-value statistics
            if self.q_table:
                q_values = list(self.q_table.values())
                stats.update({
                    'average_q_value': np.mean(q_values),
                    'max_q_value': max(q_values),
                    'min_q_value': min(q_values)
                })
        else:
            stats['avg_reward'] = 0.0
            stats['recent_performance'] = []
        
        return stats
    
    def get_top_learned_patterns(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top learned patterns from Q-table."""
        if not self.q_table:
            return []
        
        # Sort by Q-value
        sorted_patterns = sorted(self.q_table.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns[:limit]
    
    def reset_learning(self):
        """Reset Q-table and reward history."""
        self.q_table = {}
        self.reward_history = []
        self._save_q_table()
        self._save_reward_history()
        print("Learning data reset successfully.")
