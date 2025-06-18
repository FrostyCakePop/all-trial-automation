import streamlit as st
import sqlite3
import pandas as pd
import random
import time
from datetime import datetime, timedelta
import os
import smtplib

def send_sms_alert(message):
    # Your Gmail credentials
    sender_email = "vincentpsison@gmail.com"
    app_password = "jwpqxygyelddcslm"  # Your 16-digit app password (no spaces)
    
    # T-Mobile SMS email
    receiver_sms = "6614369984@tmomail.net"
    
    # Send message
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_sms, f"Subject: ALL Trial Alert\n{message}")

class AccountWarmer:
    def __init__(self):
        self.db_path = os.path.join('..', 'data', 'accounts.db')
        self.warming_activities = {
            'phase_1': ['google_search', 'youtube_watch', 'gmail_check'],
            'phase_2': ['local_business_review', 'maps_search', 'shopping_browse'],
            'phase_3': ['multiple_reviews', 'content_engagement', 'profile_updates'],
            'phase_4': ['ready_for_legal_reviews']
        }
    
    def start_warming_schedule(self):
        """Start automated warming schedule"""
        st.success("✅ Warming schedule started!")
        st.info("Warming process is now running in the background")
        
        # Simulate warming activities
        self.run_warming_cycle()
    
    def run_warming_cycle(self):
        """Execute warming activities for eligible accounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get accounts ready for warming
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE status IN ('created', 'warming') 
                AND (last_activity IS NULL OR last_activity < date('now', '-4 hours'))
            """)
            
            accounts = cursor.fetchall()
            
            if accounts:
                for account in accounts:
                    self.warm_single_account(account)
                st.success(f"Warming cycle completed for {len(accounts)} accounts")
            else:
                st.info("No accounts ready for warming")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Warming cycle error: {str(e)}")
    
    def warm_single_account(self, account):
        """Warm a single account based on its current phase"""
        account_id = account[0]
        warming_phase = account[8] if len(account) > 8 else 1
        
        activities = self.warming_activities[f'phase_{warming_phase}']
        activity = random.choice(activities)
        
        # Simulate activity execution
        success = random.random() > 0.1  # 90% success rate
        
        # Log activity
        self.log_warming_activity(account_id, activity, success)
        
        # Update account progress
        if success:
            self.update_account_progress(account_id, warming_phase)

    def log_warming_activity(self, account_id, activity, success):
        """Log warming activity to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO warming_activities 
                (account_id, activity_type, activity_date, success, details)
                VALUES (?, ?, datetime('now'), ?, ?)
            """, (account_id, activity, success, f"Executed {activity}"))
            
            conn.commit()
            conn.close()
            
            # Send SMS alert for successful activities
            if success:
                send_sms_alert(f"Account {account_id} completed {activity}")
                
        except Exception as e:
            st.error(f"Logging error: {str(e)}")

    def update_account_progress(self, account_id, current_phase):
        """Update account warming progress"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update last activity
            cursor.execute("""
                UPDATE accounts 
                SET last_activity = datetime('now'), status = 'warming'
                WHERE id = ?
            """, (account_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Progress update error: {str(e)}")

def main():
    st.set_page_config(
        page_title="ALL Trial Lawyers - Account Warmer",
        page_icon="🌡️",
        layout="wide"
    )
    
    st.title("🌡️ ALL Trial Lawyers Account Warmer")
    st.markdown("**Automated account warming system**")
    
    # Initialize warmer
    warmer = AccountWarmer()
    
    # Control panel
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎛️ Warming Controls")
        
        if st.button("▶️ Start Warming Process", type="primary"):
            warmer.start_warming_schedule()
        
        if st.button("⏸️ Pause Warming"):
            st.info("Warming paused")
        
        if st.button("🔄 Force Warming Cycle"):
            warmer.run_warming_cycle()
        
        # Warming configuration
        st.subheader("⚙️ Warming Settings")
        
        phase_1_duration = st.number_input("Phase 1 Duration (days)", value=3)
        phase_2_duration = st.number_input("Phase 2 Duration (days)", value=4)
        phase_3_duration = st.number_input("Phase 3 Duration (days)", value=7)
        
        daily_activities = st.number_input("Daily Activities per Account", value=3)
    
    with col2:
        st.subheader("📈 Warming Progress")
        display_warming_progress(warmer)

def display_warming_progress(warmer):
    """Show warming progress for all accounts"""
    try:
        conn = sqlite3.connect(warmer.db_path)
        
        warming_df = pd.read_sql_query("""
            SELECT 
                email,
                platform,
                warming_phase,
                status,
                creation_date,
                last_activity,
                CASE 
                    WHEN warming_phase = 1 THEN 'Setting up activity patterns'
                    WHEN warming_phase = 2 THEN 'Building local engagement'
                    WHEN warming_phase = 3 THEN 'Increasing activity volume'
                    WHEN warming_phase = 4 THEN 'Ready for legal reviews'
                    ELSE 'Initial setup'
                END as phase_description
            FROM accounts
            WHERE status IN ('warming', 'ready', 'created')
            ORDER BY creation_date DESC
        """, conn)
        
        if not warming_df.empty:
            st.dataframe(warming_df, use_container_width=True)
            
            # Live activity updates
            st.subheader("🔴 Live Activity Feed")
            recent_activities = pd.read_sql_query("""
                SELECT 
                    a.email,
                    wa.activity_type,
                    wa.activity_date,
                    wa.success
                FROM warming_activities wa
                JOIN accounts a ON wa.account_id = a.id
                ORDER BY wa.activity_date DESC
                LIMIT 5
            """, conn)
            
            if not recent_activities.empty:
                st.dataframe(recent_activities)
            else:
                st.info("No recent activities")
            
            # Statistics
            st.subheader("📊 Warming Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_accounts = len(warming_df)
                st.metric("Total Accounts", total_accounts)
            
            with col2:
                warming_accounts = len(warming_df[warming_df['status'] == 'warming'])
                st.metric("Currently Warming", warming_accounts)
            
            with col3:
                ready_accounts = len(warming_df[warming_df['status'] == 'ready'])
                st.metric("Ready for Reviews", ready_accounts)
        else:
            st.info("No accounts found. Create accounts first using the Account Creator.")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Progress display error: {str(e)}")

if __name__ == "__main__":
    main()
