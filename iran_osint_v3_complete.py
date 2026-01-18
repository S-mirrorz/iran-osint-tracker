#!/usr/bin/env python3
"""
Iran OSINT Tracker v3.0 - Complete Enhanced Edition
Open Source Intelligence Platform for Iran Research & Accountability

COMPLETE FEATURES (v3.0):
    • Investigate - Add subjects, generate search URLs
    • Subjects - Track investigation subjects with status/risk levels
    • Databases - Sanctions, Corporate, Iran-specific resources
    • How To - Security & safety guide for investigators
    • Monitor - Track Twitter accounts and news sources (10 each)
    • References - Document and cite findings
    • Contacts - Directory of organizations that can help
    
    NEW IN v3.0:
    • Follow the Money - Financial investigation tools & resources
    • Internet Status - Iran connectivity monitoring tools
    • Photo/Video Verification - Image forensics & verification tools
    • Enhanced database resources

JAVASCRIPT FIXES INCLUDED:
    • Fixed showSection() event handling
    • Fixed viewSubject() quote escaping with template literals
    • Added try-catch error handling for API calls
    • Added escapeHtml() for XSS prevention

LICENSE: MIT - Free for journalism, research, and human rights documentation
"""

import os
import sys
import json
import sqlite3
import hashlib
import argparse
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from urllib.parse import quote, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Config:
    """Master configuration for Iran OSINT Tracker"""
    
    APP_NAME: str = "Iran OSINT Tracker"
    VERSION: str = "3.0.0"
    
    BASE_DIR: Path = field(default_factory=lambda: Path.home() / "iran_osint")
    DB_PATH: Path = field(default_factory=lambda: Path.home() / "iran_osint" / "database.db")
    EXPORTS_PATH: Path = field(default_factory=lambda: Path.home() / "iran_osint" / "exports")
    
    # IRGC-affiliated entities for flagging
    IRGC_ENTITIES: List[str] = field(default_factory=lambda: [
        "Mahan Air", "Iran Air", "Qeshm Air", "SAHA Airlines",
        "Bank Melli", "Bank Mellat", "Bank Saderat", "Bank Sepah",
        "Khatam al-Anbiya", "MAPNA Group", "Bonyad Mostazafan",
        "IRISL", "NITC", "NIOC", "NIGC", "IRGC", "Quds Force",
        "Basij", "MODAFL", "Iran Electronics Industries",
    ])
    
    # Universities with known military/intelligence connections
    FLAGGED_UNIVERSITIES: List[str] = field(default_factory=lambda: [
        "Imam Hossein University", "Malek Ashtar University",
        "Sharif University of Technology", "Shahid Beheshti University",
        "Iran University of Science and Technology",
    ])
    
    # Preset contacts for quick reference
    CONTACTS: List[Dict] = field(default_factory=lambda: [
        {"name": "Amnesty International - Iran", "type": "Human Rights", "contact": "iran@amnesty.org", "url": "https://www.amnesty.org/en/location/middle-east-and-north-africa/iran/", "description": "Global human rights organization"},
        {"name": "Human Rights Watch - Iran", "type": "Human Rights", "contact": "hrwpress@hrw.org", "url": "https://www.hrw.org/middle-east/n-africa/iran", "description": "Reports on human rights abuses"},
        {"name": "Iran Human Rights (IHR)", "type": "Human Rights", "contact": "info@iranhr.net", "url": "https://iranhr.net/en/", "description": "Norway-based documentation"},
        {"name": "Center for Human Rights in Iran", "type": "Human Rights", "contact": "info@iranhumanrights.org", "url": "https://iranhumanrights.org/", "description": "Independent research"},
        {"name": "Bellingcat", "type": "Journalism", "contact": "contact@bellingcat.com", "url": "https://www.bellingcat.com/", "description": "Open source investigations"},
        {"name": "OCCRP", "type": "Journalism", "contact": "info@occrp.org", "url": "https://www.occrp.org/", "description": "Investigative journalism"},
        {"name": "OFAC (US Treasury)", "type": "Government", "contact": "ofac_feedback@treasury.gov", "url": "https://home.treasury.gov/", "description": "US sanctions"},
        {"name": "Access Now Helpline", "type": "Digital Security", "contact": "help@accessnow.org", "url": "https://www.accessnow.org/help/", "description": "24/7 digital security"},
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        # Subjects table - main investigation targets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_fa TEXT,
                aliases TEXT,
                location_spotted TEXT,
                country TEXT,
                event_description TEXT,
                linkedin_url TEXT,
                linkedin_headline TEXT,
                linkedin_companies TEXT,
                linkedin_education TEXT,
                twitter_url TEXT,
                sanctions_checked INTEGER DEFAULT 0,
                sanctions_hits TEXT,
                risk_level TEXT DEFAULT 'Unknown',
                risk_indicators TEXT,
                status TEXT DEFAULT 'New',
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Twitter accounts to monitor (max 10)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS twitter_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT,
                description TEXT,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        
        # News sources to monitor (max 10)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                category TEXT,
                language TEXT DEFAULT 'en',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        
        # Findings/References - documented discoveries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                finding_type TEXT,
                description TEXT,
                source_url TEXT,
                source_name TEXT,
                subject_id INTEGER,
                tags TEXT,
                importance TEXT DEFAULT 'Medium',
                verified INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)
        
        # User-added contacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_type TEXT,
                email TEXT,
                phone TEXT,
                url TEXT,
                description TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def insert(self, table: str, data: Dict) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(data.values()))
        self.conn.commit()
        return cursor.lastrowid
    
    def update(self, table: str, record_id: int, data: Dict):
        updates = ", ".join([f"{k} = ?" for k in data.keys()])
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE {table} SET {updates} WHERE id = ?", list(data.values()) + [record_id])
        self.conn.commit()
    
    def delete(self, table: str, record_id: int):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        self.conn.commit()
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def query_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        results = self.query(sql, params)
        return results[0] if results else None
    
    def count(self, table: str) -> int:
        result = self.query_one(f"SELECT COUNT(*) as count FROM {table}")
        return result["count"] if result else 0


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SearchGenerator:
    """Generate OSINT search URLs for various platforms"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate_all(self, name: str, name_fa: str = "", company: str = "") -> Dict[str, Dict[str, str]]:
        """Generate comprehensive search URLs for a subject"""
        urls = {}
        
        # LinkedIn searches
        urls["linkedin"] = {
            "people_search": f"https://www.linkedin.com/search/results/people/?keywords={quote(name)}",
            "google_public": f"https://www.google.com/search?q={quote(f'site:linkedin.com/in \"{name}\"')}",
            "iran_connection": f"https://www.google.com/search?q={quote(f'site:linkedin.com/in \"{name}\" (Iran OR Tehran OR IRGC)')}",
        }
        
        # Sanctions databases
        urls["sanctions"] = {
            "ofac": f"https://sanctionssearch.ofac.treas.gov/Details.aspx?id={quote(name)}",
            "opensanctions": f"https://www.opensanctions.org/search/?q={quote(name)}",
            "uk_sanctions": f"https://search-uk-sanctions-list.service.gov.uk/?searchTerm={quote(name)}",
            "eu_sanctions": f"https://www.sanctionsmap.eu/#/main?search={quote(name)}",
        }
        
        # Corporate registries
        urls["corporate"] = {
            "opencorporates": f"https://opencorporates.com/companies?q={quote(name)}",
            "uk_companies": f"https://find-and-update.company-information.service.gov.uk/search?q={quote(name)}",
            "icij_offshore": f"https://offshoreleaks.icij.org/search?q={quote(name)}",
        }
        
        # Social media
        urls["social_media"] = {
            "twitter": f"https://twitter.com/search?q={quote(name)}&f=user",
            "instagram": f"https://www.google.com/search?q={quote(f'site:instagram.com \"{name}\"')}",
            "facebook": f"https://www.google.com/search?q={quote(f'site:facebook.com \"{name}\"')}",
        }
        
        # General web search
        urls["web_search"] = {
            "google": f"https://www.google.com/search?q={quote(name)}",
            "google_news": f"https://www.google.com/search?q={quote(name)}&tbm=nws",
            "duckduckgo": f"https://duckduckgo.com/?q={quote(name)}",
        }
        
        # Persian name searches
        if name_fa:
            urls["persian"] = {
                "google": f"https://www.google.com/search?q={quote(name_fa)}",
                "linkedin": f"https://www.linkedin.com/search/results/people/?keywords={quote(name_fa)}",
                "twitter": f"https://twitter.com/search?q={quote(name_fa)}",
            }
        
        return urls


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGERS
# ═══════════════════════════════════════════════════════════════════════════════

class SubjectManager:
    """Manage investigation subjects"""
    
    def __init__(self, db: Database, config: Config):
        self.db = db
        self.config = config
    
    def add(self, name_en: str, name_fa: str = "", location: str = "", 
            event: str = "", notes: str = "") -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        subject_id = self.db.insert("subjects", {
            "name_en": name_en, "name_fa": name_fa,
            "location_spotted": location, "event_description": event,
            "notes": notes, "status": "New", "risk_level": "Unknown",
            "created_at": now,
        })
        return {"status": "success", "id": subject_id, "name": name_en}
    
    def get(self, subject_id: int) -> Optional[Dict]:
        return self.db.query_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    
    def get_all(self, status: str = None, risk_level: str = None) -> List[Dict]:
        sql = "SELECT * FROM subjects WHERE 1=1"
        params = []
        if status:
            sql += " AND status = ?"
            params.append(status)
        if risk_level:
            sql += " AND risk_level = ?"
            params.append(risk_level)
        sql += " ORDER BY created_at DESC"
        return self.db.query(sql, tuple(params))
    
    def update(self, subject_id: int, **kwargs) -> Dict:
        kwargs["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.db.update("subjects", subject_id, kwargs)
        return {"status": "success", "id": subject_id}
    
    def delete(self, subject_id: int) -> Dict:
        self.db.delete("subjects", subject_id)
        return {"status": "success", "id": subject_id}
    
    def get_statistics(self) -> Dict:
        total = self.db.query_one("SELECT COUNT(*) as count FROM subjects")["count"]
        by_status = self.db.query("SELECT status, COUNT(*) as count FROM subjects GROUP BY status")
        by_risk = self.db.query("SELECT risk_level, COUNT(*) as count FROM subjects GROUP BY risk_level")
        return {
            "total": total,
            "by_status": {r["status"]: r["count"] for r in by_status},
            "by_risk": {r["risk_level"]: r["count"] for r in by_risk},
        }


class MonitorManager:
    """Manage monitored Twitter accounts and news sources"""
    
    MAX_TWITTER = 10
    MAX_NEWS = 10
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_twitter(self, username: str, description: str = "") -> Dict:
        username = username.lstrip("@").strip()
        if self.db.count("twitter_accounts") >= self.MAX_TWITTER:
            return {"status": "error", "message": f"Maximum {self.MAX_TWITTER} accounts reached"}
        existing = self.db.query_one("SELECT id FROM twitter_accounts WHERE username = ?", (username,))
        if existing:
            return {"status": "error", "message": "Account already exists"}
        aid = self.db.insert("twitter_accounts", {
            "username": username, "description": description,
            "is_active": 1, "created_at": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "success", "id": aid, "username": username}
    
    def get_twitter(self) -> List[Dict]:
        return self.db.query("SELECT * FROM twitter_accounts WHERE is_active = 1 ORDER BY created_at DESC")
    
    def delete_twitter(self, aid: int) -> Dict:
        self.db.delete("twitter_accounts", aid)
        return {"status": "success"}
    
    def add_news(self, name: str, url: str, description: str = "") -> Dict:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        if self.db.count("news_sources") >= self.MAX_NEWS:
            return {"status": "error", "message": f"Maximum {self.MAX_NEWS} sources reached"}
        existing = self.db.query_one("SELECT id FROM news_sources WHERE url = ?", (url,))
        if existing:
            return {"status": "error", "message": "Source already exists"}
        sid = self.db.insert("news_sources", {
            "name": name, "url": url, "description": description,
            "is_active": 1, "created_at": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "success", "id": sid, "name": name}
    
    def get_news(self) -> List[Dict]:
        return self.db.query("SELECT * FROM news_sources WHERE is_active = 1 ORDER BY created_at DESC")
    
    def delete_news(self, sid: int) -> Dict:
        self.db.delete("news_sources", sid)
        return {"status": "success"}


class FindingsManager:
    """Manage documented findings and references"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add(self, title: str, finding_type: str = "", description: str = "",
            source_url: str = "", source_name: str = "", subject_id: int = None,
            tags: str = "", importance: str = "Medium") -> Dict:
        fid = self.db.insert("findings", {
            "title": title, "finding_type": finding_type, "description": description,
            "source_url": source_url, "source_name": source_name, "subject_id": subject_id,
            "tags": tags, "importance": importance, "verified": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "success", "id": fid, "title": title}
    
    def get(self, fid: int) -> Optional[Dict]:
        return self.db.query_one("SELECT * FROM findings WHERE id = ?", (fid,))
    
    def get_all(self, finding_type: str = None, importance: str = None) -> List[Dict]:
        sql = "SELECT f.*, s.name_en as subject_name FROM findings f LEFT JOIN subjects s ON f.subject_id = s.id WHERE 1=1"
        params = []
        if finding_type:
            sql += " AND f.finding_type = ?"
            params.append(finding_type)
        if importance:
            sql += " AND f.importance = ?"
            params.append(importance)
        sql += " ORDER BY f.created_at DESC"
        return self.db.query(sql, tuple(params))
    
    def verify(self, fid: int, verified: bool) -> Dict:
        self.db.update("findings", fid, {
            "verified": 1 if verified else 0,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "success"}
    
    def delete(self, fid: int) -> Dict:
        self.db.delete("findings", fid)
        return {"status": "success"}


class ContactsManager:
    """Manage preset and user-added contacts"""
    
    def __init__(self, db: Database, config: Config):
        self.db = db
        self.config = config
    
    def get_preset(self) -> List[Dict]:
        return self.config.CONTACTS
    
    def add(self, name: str, contact_type: str = "", email: str = "",
            url: str = "", description: str = "") -> Dict:
        cid = self.db.insert("user_contacts", {
            "name": name, "contact_type": contact_type, "email": email,
            "url": url, "description": description,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "success", "id": cid, "name": name}
    
    def get_user(self) -> List[Dict]:
        return self.db.query("SELECT * FROM user_contacts ORDER BY created_at DESC")
    
    def delete(self, cid: int) -> Dict:
        self.db.delete("user_contacts", cid)
        return {"status": "success"}


# ═══════════════════════════════════════════════════════════════════════════════
# HTML DASHBOARD GENERATOR - COMPLETE ENHANCED VERSION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_dashboard_html(config: Config) -> str:
    """
    Generate the complete web dashboard HTML.
    
    ENHANCED FEATURES:
    - Follow the Money section
    - Internet Status monitoring
    - Photo/Video Verification tools
    - Expanded database resources
    
    JAVASCRIPT FIXES APPLIED:
    1. showSection(id, btn) - properly receives button parameter
    2. viewSubject() - fixed quote escaping using template literals
    3. Added try-catch error handling for API calls
    4. escapeHtml() function for XSS prevention
    """
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iran OSINT Tracker v3.0 - Complete Edition</title>
    <style>
        :root { 
            --primary: #3B82F6; 
            --secondary: #10B981; 
            --warning: #F59E0B; 
            --danger: #EF4444; 
            --dark: #1F2937; 
            --darker: #111827; 
            --light: #F3F4F6; 
            --gray: #6B7280; 
            --border: #374151;
            --purple: #8B5CF6;
            --cyan: #06B6D4;
            --pink: #EC4899;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--darker); color: var(--light); line-height: 1.6; }
        
        /* Header */
        .header { background: linear-gradient(135deg, var(--dark), var(--darker)); border-bottom: 1px solid var(--border); padding: 1.5rem 2rem; position: sticky; top: 0; z-index: 100; }
        .header-content { max-width: 1600px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
        .logo { display: flex; align-items: center; gap: 0.75rem; }
        .logo-icon { font-size: 2rem; }
        .logo-text { font-size: 1.5rem; font-weight: 700; }
        .logo-subtitle { font-size: 0.8rem; color: var(--gray); }
        .nav { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .nav-btn { padding: 0.6rem 1rem; background: transparent; border: 1px solid var(--border); border-radius: 6px; color: var(--light); cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
        .nav-btn:hover { background: var(--dark); border-color: var(--primary); }
        .nav-btn.active { background: var(--primary); border-color: var(--primary); }
        
        /* Main */
        .main { max-width: 1600px; margin: 0 auto; padding: 2rem; }
        .section { display: none; }
        .section.active { display: block; }
        
        /* Grids */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem; }
        .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }
        .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; }
        
        /* Cards */
        .card { background: var(--dark); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
        .card-header { padding: 1.25rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 1rem; }
        .card-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
        .icon-blue { background: rgba(59, 130, 246, 0.2); }
        .icon-green { background: rgba(16, 185, 129, 0.2); }
        .icon-orange { background: rgba(245, 158, 11, 0.2); }
        .icon-red { background: rgba(239, 68, 68, 0.2); }
        .icon-purple { background: rgba(139, 92, 246, 0.2); }
        .icon-cyan { background: rgba(6, 182, 212, 0.2); }
        .icon-pink { background: rgba(236, 72, 153, 0.2); }
        .icon-yellow { background: rgba(234, 179, 8, 0.2); }
        .card-title { font-weight: 600; font-size: 1.1rem; }
        .card-subtitle { font-size: 0.8rem; color: var(--gray); }
        .card-body { padding: 1.25rem; }
        
        /* Forms */
        .form-group { margin-bottom: 1rem; }
        .form-label { display: block; margin-bottom: 0.4rem; font-size: 0.85rem; color: var(--gray); }
        .form-input { width: 100%; padding: 0.75rem; background: var(--darker); border: 1px solid var(--border); border-radius: 6px; color: var(--light); font-size: 0.95rem; }
        .form-input:focus { outline: none; border-color: var(--primary); }
        
        /* Buttons */
        .btn { padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #2563EB; }
        .btn-secondary { background: var(--dark); color: var(--light); border: 1px solid var(--border); }
        .btn-danger { background: var(--danger); color: white; }
        .btn-sm { padding: 0.5rem 1rem; font-size: 0.85rem; }
        .btn-block { width: 100%; justify-content: center; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.875rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-weight: 600; color: var(--gray); font-size: 0.85rem; text-transform: uppercase; }
        tr:hover { background: rgba(59, 130, 246, 0.05); }
        
        /* Badges */
        .badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 500; display: inline-block; }
        .badge-new { background: var(--primary); color: white; }
        .badge-investigating { background: var(--warning); color: var(--darker); }
        .badge-verified { background: var(--secondary); color: white; }
        .badge-unknown { background: var(--gray); color: white; }
        .badge-low { background: var(--secondary); color: white; }
        .badge-medium { background: var(--warning); color: var(--darker); }
        .badge-high { background: #F97316; color: white; }
        .badge-critical { background: var(--danger); color: white; }
        
        /* Stats */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .stat-card { background: var(--darker); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: 700; color: var(--primary); }
        .stat-label { font-size: 0.8rem; color: var(--gray); }
        
        /* Links */
        .search-category { margin-bottom: 1.5rem; }
        .search-category h4 { color: var(--primary); margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; text-transform: uppercase; }
        .search-link { display: block; padding: 0.6rem 0.875rem; background: var(--darker); border-radius: 6px; margin-bottom: 0.4rem; color: var(--light); text-decoration: none; font-size: 0.9rem; transition: all 0.2s; }
        .search-link:hover { background: rgba(59, 130, 246, 0.1); transform: translateX(4px); }
        .db-link { display: block; padding: 0.5rem 0.75rem; background: var(--darker); border-radius: 4px; margin-bottom: 0.3rem; color: var(--light); text-decoration: none; font-size: 0.85rem; transition: all 0.2s; }
        .db-link:hover { background: rgba(59, 130, 246, 0.15); }
        
        /* Scrollable */
        .scroll-box { max-height: 400px; overflow-y: auto; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.75); z-index: 1000; justify-content: center; align-items: center; padding: 1rem; }
        .modal.active { display: flex; }
        .modal-content { background: var(--dark); border: 1px solid var(--border); border-radius: 12px; width: 100%; max-width: 600px; max-height: 90vh; overflow-y: auto; }
        .modal-header { padding: 1.25rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .modal-close { background: none; border: none; color: var(--gray); font-size: 1.5rem; cursor: pointer; }
        .modal-body { padding: 1.25rem; }
        
        /* Alerts */
        .alert { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
        .alert-success { background: rgba(16, 185, 129, 0.1); border: 1px solid var(--secondary); }
        .alert-error { background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); }
        .alert-info { background: rgba(59, 130, 246, 0.1); border: 1px solid var(--primary); }
        .alert-warning { background: rgba(245, 158, 11, 0.1); border: 1px solid var(--warning); }
        
        /* Guide sections */
        .guide-section { background: var(--darker); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; }
        .guide-section h4 { color: var(--primary); margin-bottom: 0.75rem; }
        .guide-section ul { margin-left: 1.5rem; }
        .guide-section li { margin-bottom: 0.5rem; }
        .warning-box { background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); border-radius: 6px; padding: 1rem; margin: 1rem 0; }
        .tip-box { background: rgba(16, 185, 129, 0.1); border: 1px solid var(--secondary); border-radius: 6px; padding: 1rem; margin: 1rem 0; }
        .info-box { background: rgba(59, 130, 246, 0.1); border: 1px solid var(--primary); border-radius: 6px; padding: 1rem; margin: 1rem 0; }
        
        /* Monitor items */
        .monitor-item { background: var(--darker); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        .monitor-item-name { font-weight: 500; }
        .monitor-item-desc { font-size: 0.8rem; color: var(--gray); }
        .empty-state { text-align: center; padding: 2rem; color: var(--gray); }
        
        /* Contact cards */
        .contact-card { background: var(--darker); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
        .contact-name { font-weight: 600; margin-bottom: 0.25rem; }
        .contact-desc { font-size: 0.85rem; color: var(--gray); margin-bottom: 0.5rem; }
        .contact-links { display: flex; gap: 1rem; flex-wrap: wrap; }
        .contact-links a { font-size: 0.85rem; color: var(--primary); text-decoration: none; }
        
        /* Finding cards */
        .finding-card { background: var(--darker); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
        .finding-title { font-weight: 600; }
        .finding-meta { font-size: 0.8rem; color: var(--gray); margin: 0.5rem 0; }
        
        /* Status indicators */
        .status-indicator { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.85rem; }
        .status-online { background: rgba(16, 185, 129, 0.2); color: var(--secondary); }
        .status-disrupted { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .status-offline { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        
        /* Tool cards */
        .tool-card { background: var(--darker); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; transition: all 0.2s; }
        .tool-card:hover { border-color: var(--primary); transform: translateY(-2px); }
        .tool-card a { color: var(--light); text-decoration: none; }
        .tool-name { font-weight: 600; margin-bottom: 0.25rem; }
        .tool-desc { font-size: 0.8rem; color: var(--gray); }
        
        /* Footer */
        .footer { text-align: center; padding: 2rem; border-top: 1px solid var(--border); margin-top: 2rem; color: var(--gray); font-size: 0.85rem; }
        
        /* Responsive */
        @media (max-width: 768px) { 
            .grid, .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; } 
            .header-content { flex-direction: column; text-align: center; } 
            .nav { justify-content: center; } 
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-icon">🔍</span>
                <div>
                    <div class="logo-text">Iran OSINT Tracker</div>
                    <div class="logo-subtitle">Open Source Intelligence Platform v3.0 - Complete Edition</div>
                </div>
            </div>
            <nav class="nav">
                <button class="nav-btn active" onclick="showSection('investigate', this)">🔎 Investigate</button>
                <button class="nav-btn" onclick="showSection('subjects', this)">👥 Subjects</button>
                <button class="nav-btn" onclick="showSection('databases', this)">📚 Databases</button>
                <button class="nav-btn" onclick="showSection('money', this)">💰 Follow Money</button>
                <button class="nav-btn" onclick="showSection('verification', this)">📷 Verify Media</button>
                <button class="nav-btn" onclick="showSection('internet', this)">🌐 Internet Status</button>
                <button class="nav-btn" onclick="showSection('howto', this)">📖 How To</button>
                <button class="nav-btn" onclick="showSection('monitor', this)">📡 Monitor</button>
                <button class="nav-btn" onclick="showSection('references', this)">📋 References</button>
                <button class="nav-btn" onclick="showSection('contacts', this)">📞 Contacts</button>
            </nav>
        </div>
    </header>
    
    <main class="main">
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- INVESTIGATE SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="investigate" class="section active">
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">➕</div><div><div class="card-title">Add Subject</div><div class="card-subtitle">Start a new investigation</div></div></div>
                    <div class="card-body">
                        <form id="addSubjectForm">
                            <div class="form-group"><label class="form-label">Name (English) *</label><input type="text" class="form-input" id="nameEn" required placeholder="Full name"></div>
                            <div class="form-group"><label class="form-label">Name (Farsi)</label><input type="text" class="form-input" id="nameFa" placeholder="نام کامل" dir="rtl"></div>
                            <div class="form-group"><label class="form-label">Location Spotted</label><input type="text" class="form-input" id="location" placeholder="City, Country"></div>
                            <div class="form-group"><label class="form-label">Event/Context</label><input type="text" class="form-input" id="event" placeholder="Where/how identified"></div>
                            <div class="form-group"><label class="form-label">Notes</label><textarea class="form-input" id="notes" rows="2"></textarea></div>
                            <button type="submit" class="btn btn-primary btn-block">➕ Add Subject</button>
                        </form>
                        <div id="addResult" style="margin-top:1rem;"></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">🔎</div><div><div class="card-title">Generate Search URLs</div><div class="card-subtitle">Legal OSINT search links</div></div></div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="form-group"><label class="form-label">Name to Search *</label><input type="text" class="form-input" id="searchName" required placeholder="Enter name"></div>
                            <div class="form-group"><label class="form-label">Persian Name</label><input type="text" class="form-input" id="searchNameFa" placeholder="نام فارسی" dir="rtl"></div>
                            <button type="submit" class="btn btn-primary btn-block">🔎 Generate URLs</button>
                        </form>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">📊</div><div><div class="card-title">Statistics</div></div></div>
                    <div class="card-body">
                        <div class="stats-grid">
                            <div class="stat-card"><div class="stat-number" id="statTotal">0</div><div class="stat-label">Total</div></div>
                            <div class="stat-card"><div class="stat-number" id="statNew">0</div><div class="stat-label">New</div></div>
                            <div class="stat-card"><div class="stat-number" id="statInvestigating">0</div><div class="stat-label">Active</div></div>
                            <div class="stat-card"><div class="stat-number" id="statVerified">0</div><div class="stat-label">Verified</div></div>
                        </div>
                        <button class="btn btn-secondary btn-block" onclick="loadStats()">🔄 Refresh</button>
                    </div>
                </div>
            </div>
            <div id="searchResultsContainer" class="card" style="margin-top:1.5rem;display:none;">
                <div class="card-header"><div class="card-icon icon-green">🔗</div><div><div class="card-title">Search URLs</div><div class="card-subtitle" id="searchResultsFor">-</div></div></div>
                <div class="card-body"><div id="searchResults" class="scroll-box"></div></div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- SUBJECTS SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="subjects" class="section">
            <div class="card">
                <div class="card-header"><div class="card-icon icon-orange">👥</div><div><div class="card-title">Investigation Subjects</div></div></div>
                <div class="card-body">
                    <div style="margin-bottom:1rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
                        <button class="btn btn-secondary btn-sm" onclick="loadSubjects()">🔄 Refresh</button>
                        <select id="statusFilter" class="form-input" style="width:auto;" onchange="loadSubjects()">
                            <option value="">All Statuses</option><option value="New">New</option><option value="Investigating">Investigating</option><option value="Verified">Verified</option>
                        </select>
                    </div>
                    <div style="overflow-x:auto;"><table><thead><tr><th>ID</th><th>Name</th><th>Location</th><th>Status</th><th>Risk</th><th>Actions</th></tr></thead><tbody id="subjectsTable"></tbody></table></div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- DATABASES SECTION - ENHANCED -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="databases" class="section">
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">🔐</div><div><div class="card-title">Sanctions Databases</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://sanctionssearch.ofac.treas.gov/" target="_blank" class="db-link">🇺🇸 OFAC Sanctions Search (US)</a>
                        <a href="https://www.opensanctions.org/" target="_blank" class="db-link">🌍 OpenSanctions (Global)</a>
                        <a href="https://search-uk-sanctions-list.service.gov.uk/" target="_blank" class="db-link">🇬🇧 UK Sanctions List</a>
                        <a href="https://www.sanctionsmap.eu/" target="_blank" class="db-link">🇪🇺 EU Sanctions Map</a>
                        <a href="https://scsanctions.un.org/search/" target="_blank" class="db-link">🇺🇳 UN Consolidated Sanctions</a>
                        <a href="https://www.dfat.gov.au/international-relations/security/sanctions/consolidated-list" target="_blank" class="db-link">🇦🇺 Australia Sanctions</a>
                        <a href="https://www.international.gc.ca/world-monde/international_relations-relations_internationales/sanctions/consolidated-consolide.aspx" target="_blank" class="db-link">🇨🇦 Canada Sanctions</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">🏢</div><div><div class="card-title">Corporate Registries</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://opencorporates.com/" target="_blank" class="db-link">🌐 OpenCorporates (Global)</a>
                        <a href="https://find-and-update.company-information.service.gov.uk/" target="_blank" class="db-link">🇬🇧 UK Companies House</a>
                        <a href="https://offshoreleaks.icij.org/" target="_blank" class="db-link">🌴 ICIJ Offshore Leaks</a>
                        <a href="https://egrul.nalog.ru/" target="_blank" class="db-link">🇷🇺 Russia EGRUL</a>
                        <a href="https://www.sec.gov/cgi-bin/browse-edgar" target="_blank" class="db-link">🇺🇸 SEC EDGAR</a>
                        <a href="https://www.dubaided.gov.ae/" target="_blank" class="db-link">🇦🇪 Dubai Business</a>
                        <a href="https://www.zefix.ch/en/search/entity/welcome" target="_blank" class="db-link">🇨🇭 Swiss Companies</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">🇮🇷</div><div><div class="card-title">Iran-Specific Resources</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://www.iranwatch.org/iranian-entities" target="_blank" class="db-link">📋 IranWatch Entities Database</a>
                        <a href="https://iranhr.net/en/" target="_blank" class="db-link">⚖️ Iran Human Rights (IHR)</a>
                        <a href="https://www.hrw.org/middle-east/n-africa/iran" target="_blank" class="db-link">👁️ Human Rights Watch - Iran</a>
                        <a href="https://www.unitedagainstnucleariran.com/" target="_blank" class="db-link">☢️ United Against Nuclear Iran</a>
                        <a href="https://tavaana.org/" target="_blank" class="db-link">📚 Tavaana - Civic Education</a>
                        <a href="https://en.radiofarda.com/" target="_blank" class="db-link">📻 Radio Farda</a>
                        <a href="https://www.iranintl.com/en" target="_blank" class="db-link">📺 Iran International</a>
                        <a href="https://www.bbc.com/persian" target="_blank" class="db-link">📰 BBC Persian</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-orange">🛠️</div><div><div class="card-title">OSINT Tools</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://web.archive.org/" target="_blank" class="db-link">🏛️ Wayback Machine</a>
                        <a href="https://archive.today/" target="_blank" class="db-link">📄 Archive.today</a>
                        <a href="https://hunter.io/" target="_blank" class="db-link">📧 Hunter.io (Email finder)</a>
                        <a href="https://www.shodan.io/" target="_blank" class="db-link">🔍 Shodan (IoT Search)</a>
                        <a href="https://www.maltego.com/" target="_blank" class="db-link">🕸️ Maltego (Link Analysis)</a>
                        <a href="https://www.spokeo.com/" target="_blank" class="db-link">👤 Spokeo (People Search)</a>
                        <a href="https://namechk.com/" target="_blank" class="db-link">✅ Namechk (Username Search)</a>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- NEW: FOLLOW THE MONEY SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="money" class="section">
            <div class="alert alert-info" style="margin-bottom:1.5rem;">💰 <strong>Follow the Money:</strong> Tools and resources for tracing financial connections, shell companies, and illicit finance networks linked to the Iranian regime.</div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-yellow">🏦</div><div><div class="card-title">Financial Investigation</div><div class="card-subtitle">Banking & Money Flow</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://offshoreleaks.icij.org/" target="_blank" class="db-link">🌴 ICIJ Offshore Leaks Database</a>
                        <a href="https://www.opensanctions.org/" target="_blank" class="db-link">🔐 OpenSanctions</a>
                        <a href="https://www.fincen.gov/" target="_blank" class="db-link">🇺🇸 FinCEN (US Financial Crimes)</a>
                        <a href="https://www.fatf-gafi.org/" target="_blank" class="db-link">🌐 FATF (Anti-Money Laundering)</a>
                        <a href="https://www.treasury.gov/resource-center/sanctions/SDN-List/Pages/default.aspx" target="_blank" class="db-link">📋 SDN List (Treasury)</a>
                        <a href="https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern" target="_blank" class="db-link">🏭 BIS Entity List</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">🕵️</div><div><div class="card-title">Shell Company Research</div><div class="card-subtitle">Corporate Structure Analysis</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://opencorporates.com/" target="_blank" class="db-link">🏢 OpenCorporates</a>
                        <a href="https://www.gleif.org/en/lei-data/search" target="_blank" class="db-link">🔢 GLEIF LEI Search</a>
                        <a href="https://aleph.occrp.org/" target="_blank" class="db-link">🔍 OCCRP Aleph (Data Archive)</a>
                        <a href="https://linkedIn.com" target="_blank" class="db-link">💼 LinkedIn (Company Research)</a>
                        <a href="https://www.dnb.com/" target="_blank" class="db-link">📊 D&B Business Directory</a>
                        <a href="https://www.orbis.bvdinfo.com/" target="_blank" class="db-link">🌐 Orbis (Bureau van Dijk)</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">🚢</div><div><div class="card-title">Trade & Shipping</div><div class="card-subtitle">Import/Export & Vessels</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://www.marinetraffic.com/" target="_blank" class="db-link">🚢 MarineTraffic (Ship Tracking)</a>
                        <a href="https://www.vesselfinder.com/" target="_blank" class="db-link">📍 VesselFinder</a>
                        <a href="https://www.equasis.org/" target="_blank" class="db-link">⚓ Equasis (Ship Database)</a>
                        <a href="https://importyeti.com/" target="_blank" class="db-link">📦 ImportYeti (US Imports)</a>
                        <a href="https://www.panjiva.com/" target="_blank" class="db-link">🌐 Panjiva (Trade Data)</a>
                        <a href="https://www.flightradar24.com/" target="_blank" class="db-link">✈️ FlightRadar24</a>
                        <a href="https://www.adsbexchange.com/" target="_blank" class="db-link">🛩️ ADS-B Exchange</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-cyan">🏠</div><div><div class="card-title">Property & Assets</div><div class="card-subtitle">Real Estate Research</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://search.hm.land.gov.uk/search/property-register" target="_blank" class="db-link">🇬🇧 UK Land Registry</a>
                        <a href="https://www.zillow.com/" target="_blank" class="db-link">🇺🇸 Zillow (US Property)</a>
                        <a href="https://www.redfin.com/" target="_blank" class="db-link">🏡 Redfin (US Real Estate)</a>
                        <a href="https://propertydata.gov.uk/" target="_blank" class="db-link">🏛️ UK Property Data</a>
                        <a href="https://www.zoopla.co.uk/" target="_blank" class="db-link">🔍 Zoopla (UK Property)</a>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top:1.5rem;">
                <div class="card-header"><div class="card-icon icon-orange">⚠️</div><div><div class="card-title">Known IRGC-Linked Entities</div><div class="card-subtitle">Reference list of sanctioned/flagged organizations</div></div></div>
                <div class="card-body">
                    <div class="grid-4">
                        <div class="guide-section">
                            <h4>🏦 Banks</h4>
                            <ul>
                                <li>Bank Melli Iran</li>
                                <li>Bank Mellat</li>
                                <li>Bank Saderat</li>
                                <li>Bank Sepah</li>
                                <li>Parsian Bank</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>✈️ Airlines</h4>
                            <ul>
                                <li>Mahan Air</li>
                                <li>Iran Air</li>
                                <li>Qeshm Air</li>
                                <li>SAHA Airlines</li>
                                <li>Pouya Air</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>🏭 Conglomerates</h4>
                            <ul>
                                <li>Khatam al-Anbiya</li>
                                <li>Bonyad Mostazafan</li>
                                <li>MAPNA Group</li>
                                <li>Iran Electronics Industries</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>🚢 Shipping</h4>
                            <ul>
                                <li>IRISL (Islamic Republic Iran Shipping Lines)</li>
                                <li>NITC (National Iranian Tanker Co)</li>
                                <li>NIOC (National Iranian Oil Co)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- NEW: PHOTO/VIDEO VERIFICATION SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="verification" class="section">
            <div class="alert alert-info" style="margin-bottom:1.5rem;">📷 <strong>Media Verification:</strong> Tools for verifying photos, videos, and detecting manipulated content. Essential for documenting human rights abuses.</div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">🔍</div><div><div class="card-title">Reverse Image Search</div><div class="card-subtitle">Find image origins & copies</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://images.google.com/" target="_blank" class="db-link">🔎 Google Images (Reverse Search)</a>
                        <a href="https://yandex.com/images/" target="_blank" class="db-link">🔎 Yandex Images (Best for faces)</a>
                        <a href="https://tineye.com/" target="_blank" class="db-link">👁️ TinEye (Image tracking)</a>
                        <a href="https://www.bing.com/visualsearch" target="_blank" class="db-link">🔍 Bing Visual Search</a>
                        <a href="https://pimeyes.com/" target="_blank" class="db-link">👤 PimEyes (Face Search)</a>
                        <a href="https://www.duplichecker.com/reverse-image-search.php" target="_blank" class="db-link">🖼️ DupliChecker</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">📍</div><div><div class="card-title">Geolocation Tools</div><div class="card-subtitle">Verify photo/video locations</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://www.google.com/maps" target="_blank" class="db-link">🗺️ Google Maps</a>
                        <a href="https://earth.google.com/web/" target="_blank" class="db-link">🌍 Google Earth Web</a>
                        <a href="https://www.bing.com/maps" target="_blank" class="db-link">🗺️ Bing Maps</a>
                        <a href="https://yandex.com/maps" target="_blank" class="db-link">🗺️ Yandex Maps</a>
                        <a href="https://www.openstreetmap.org/" target="_blank" class="db-link">🗺️ OpenStreetMap</a>
                        <a href="https://www.suncalc.org/" target="_blank" class="db-link">☀️ SunCalc (Shadow analysis)</a>
                        <a href="https://www.timeanddate.com/sun/" target="_blank" class="db-link">🌅 TimeAndDate Sun Position</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">🔬</div><div><div class="card-title">Image Forensics</div><div class="card-subtitle">Detect manipulation & metadata</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://fotoforensics.com/" target="_blank" class="db-link">🔬 FotoForensics (ELA Analysis)</a>
                        <a href="https://www.metadata2go.com/" target="_blank" class="db-link">📊 Metadata2Go (EXIF viewer)</a>
                        <a href="http://exif.regex.info/exif.cgi" target="_blank" class="db-link">📋 Jeffrey's EXIF Viewer</a>
                        <a href="https://29a.ch/photo-forensics/" target="_blank" class="db-link">🔍 Forensically (Image analysis)</a>
                        <a href="https://www.imageidentify.com/" target="_blank" class="db-link">🏷️ Image Identifier</a>
                        <a href="https://www.verexif.com/en/" target="_blank" class="db-link">📄 Ver Exif (Remove/View EXIF)</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">🎥</div><div><div class="card-title">Video Verification</div><div class="card-subtitle">Analyze video content</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://citizenevidence.amnestyusa.org/" target="_blank" class="db-link">🎬 Amnesty YouTube DataViewer</a>
                        <a href="https://www.invid-project.eu/tools-and-services/invid-verification-plugin/" target="_blank" class="db-link">🔌 InVID Verification Plugin</a>
                        <a href="https://www.youtube.com/" target="_blank" class="db-link">📺 YouTube (Upload date check)</a>
                        <a href="https://www.watchframebyframe.com/" target="_blank" class="db-link">🎞️ Watch Frame by Frame</a>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top:1.5rem;">
                <div class="card-header"><div class="card-icon icon-cyan">📖</div><div><div class="card-title">Verification Methodology</div><div class="card-subtitle">Berkeley Protocol for Digital Evidence</div></div></div>
                <div class="card-body">
                    <div class="grid-2">
                        <div class="guide-section">
                            <h4>🔍 Step 1: Source Check</h4>
                            <ul>
                                <li>Who uploaded/shared the content?</li>
                                <li>When was it first posted?</li>
                                <li>Reverse image search for earlier versions</li>
                                <li>Check account history & credibility</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>📍 Step 2: Geolocation</h4>
                            <ul>
                                <li>Identify landmarks, signs, buildings</li>
                                <li>Compare with satellite imagery</li>
                                <li>Use Street View for verification</li>
                                <li>Check sun position/shadows</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>🕐 Step 3: Chronolocation</h4>
                            <ul>
                                <li>Analyze shadows for time of day</li>
                                <li>Cross-reference weather data</li>
                                <li>Check for anachronistic elements</li>
                                <li>Compare with known timeline events</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>🔬 Step 4: Forensic Analysis</h4>
                            <ul>
                                <li>Check EXIF metadata</li>
                                <li>Run Error Level Analysis (ELA)</li>
                                <li>Look for manipulation artifacts</li>
                                <li>Verify consistency across frames (video)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- NEW: INTERNET STATUS SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="internet" class="section">
            <div class="alert alert-warning" style="margin-bottom:1.5rem;">🌐 <strong>Iran Internet Status:</strong> Monitor connectivity disruptions, shutdowns, and censorship in Iran. Critical during protests and crackdowns.</div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">📊</div><div><div class="card-title">Real-Time Monitoring</div><div class="card-subtitle">Live internet status</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://ioda.inetintel.cc.gatech.edu/country/IR" target="_blank" class="db-link">📈 IODA - Internet Outage Detection (Iran)</a>
                        <a href="https://radar.cloudflare.com/ir" target="_blank" class="db-link">☁️ Cloudflare Radar - Iran</a>
                        <a href="https://ooni.org/country/IR" target="_blank" class="db-link">🔬 OONI - Iran Censorship Data</a>
                        <a href="https://www.thousandeyes.com/outages" target="_blank" class="db-link">👁️ ThousandEyes Outage Map</a>
                        <a href="https://downdetector.com/" target="_blank" class="db-link">⚠️ DownDetector</a>
                        <a href="https://netblocks.org/reports" target="_blank" class="db-link">🌐 NetBlocks Reports</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">🔒</div><div><div class="card-title">Censorship Testing</div><div class="card-subtitle">Check what's blocked</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://explorer.ooni.org/search?probe_cc=IR" target="_blank" class="db-link">🔬 OONI Explorer - Iran Tests</a>
                        <a href="https://censored.planet/" target="_blank" class="db-link">🌍 Censored Planet</a>
                        <a href="https://www.accessnow.org/keepiton/" target="_blank" class="db-link">📢 #KeepItOn Coalition</a>
                        <a href="https://filterwatch.ir/" target="_blank" class="db-link">🚫 FilterWatch Iran</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">🛡️</div><div><div class="card-title">Circumvention Tools</div><div class="card-subtitle">Help Iranians stay connected</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://signal.org/" target="_blank" class="db-link">💬 Signal (Encrypted messaging)</a>
                        <a href="https://www.torproject.org/" target="_blank" class="db-link">🧅 Tor Project</a>
                        <a href="https://psiphon.ca/" target="_blank" class="db-link">🔓 Psiphon</a>
                        <a href="https://lantern.io/" target="_blank" class="db-link">💡 Lantern</a>
                        <a href="https://protonvpn.com/" target="_blank" class="db-link">🛡️ ProtonVPN</a>
                        <a href="https://snowflake.torproject.org/" target="_blank" class="db-link">❄️ Tor Snowflake (Help proxy)</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">📰</div><div><div class="card-title">Shutdown Tracking</div><div class="card-subtitle">Historical data & reports</div></div></div>
                    <div class="card-body scroll-box">
                        <a href="https://www.accessnow.org/cms/assets/uploads/2023/03/2022-Shutdown-Report.pdf" target="_blank" class="db-link">📄 Access Now Shutdown Report 2022</a>
                        <a href="https://freedomhouse.org/country/iran/freedom-net" target="_blank" class="db-link">🗽 Freedom House - Iran</a>
                        <a href="https://www.top10vpn.com/research/cost-of-internet-shutdowns/" target="_blank" class="db-link">💰 Cost of Shutdowns Tracker</a>
                        <a href="https://ipi.media/iran/" target="_blank" class="db-link">📰 International Press Institute</a>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top:1.5rem;">
                <div class="card-header"><div class="card-icon icon-orange">📱</div><div><div class="card-title">Platform Status Reference</div><div class="card-subtitle">Commonly blocked services in Iran</div></div></div>
                <div class="card-body">
                    <div class="grid-4">
                        <div class="guide-section">
                            <h4>🚫 Usually Blocked</h4>
                            <ul>
                                <li>Twitter/X</li>
                                <li>Facebook</li>
                                <li>YouTube</li>
                                <li>Telegram</li>
                                <li>Signal</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>⚠️ Intermittently Blocked</h4>
                            <ul>
                                <li>Instagram</li>
                                <li>WhatsApp</li>
                                <li>LinkedIn</li>
                                <li>VPN services</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>✅ Often Available</h4>
                            <ul>
                                <li>Email services</li>
                                <li>Some news sites</li>
                                <li>Academic sites</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>⏰ Shutdown Times</h4>
                            <ul>
                                <li>Protests/unrest</li>
                                <li>Elections</li>
                                <li>Anniversaries</li>
                                <li>Religious events</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- HOW TO SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="howto" class="section">
            <div class="card" style="margin-bottom:1.5rem;">
                <div class="card-header"><div class="card-icon icon-cyan">📖</div><div><div class="card-title">Security & Safety Guide</div><div class="card-subtitle">Essential practices for OSINT investigators</div></div></div>
                <div class="card-body">
                    <div class="warning-box">⚠️ <strong>Important:</strong> Investigating regime-affiliated individuals can put you at risk. The Iranian government actively monitors diaspora activities. Follow these security practices.</div>
                </div>
            </div>
            <div class="grid-2">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">🔒</div><div><div class="card-title">VPN & Connection Security</div></div></div>
                    <div class="card-body">
                        <div class="guide-section">
                            <h4>🛡️ Always Use a VPN</h4>
                            <p>A VPN masks your IP address and encrypts traffic.</p>
                            <ul>
                                <li><strong>Mullvad</strong> - No email required, accepts cash</li>
                                <li><strong>ProtonVPN</strong> - Swiss-based, strong privacy</li>
                                <li><strong>IVPN</strong> - Privacy-focused</li>
                            </ul>
                            <div class="tip-box">💡 Use servers in Switzerland, Iceland, or Sweden for best privacy.</div>
                        </div>
                        <div class="guide-section">
                            <h4>🌐 Tor Browser</h4>
                            <p>For highly sensitive research, use Tor Browser.</p>
                            <ul>
                                <li>Download from: torproject.org</li>
                                <li>Use bridges in censored regions</li>
                                <li>Don't use for accounts linked to real identity</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">👤</div><div><div class="card-title">Identity Protection</div></div></div>
                    <div class="card-body">
                        <div class="guide-section">
                            <h4>🎭 Research Personas</h4>
                            <ul>
                                <li>Create dedicated research accounts</li>
                                <li>Use separate browser profiles</li>
                                <li>Consider a dedicated device</li>
                                <li>Never log into personal accounts during research</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>📧 Secure Email</h4>
                            <ul>
                                <li><strong>ProtonMail</strong> - End-to-end encrypted</li>
                                <li><strong>Tutanota</strong> - German-based, encrypted</li>
                                <li>Use unique passwords (password manager)</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">🌐</div><div><div class="card-title">Browser Security</div></div></div>
                    <div class="card-body">
                        <div class="guide-section">
                            <h4>🔐 Browser Recommendations</h4>
                            <ul>
                                <li><strong>Firefox</strong> with privacy extensions</li>
                                <li><strong>Brave</strong> - Built-in ad blocking</li>
                                <li><strong>Tor Browser</strong> - Maximum anonymity</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>🧩 Essential Extensions</h4>
                            <ul>
                                <li><strong>uBlock Origin</strong> - Ad/tracker blocking</li>
                                <li><strong>Privacy Badger</strong> - Intelligent blocking</li>
                                <li><strong>HTTPS Everywhere</strong> - Force encryption</li>
                                <li><strong>Container tabs</strong> - Isolate sessions</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">⚔️</div><div><div class="card-title">Operational Security</div></div></div>
                    <div class="card-body">
                        <div class="guide-section">
                            <h4>🚨 Threat Awareness</h4>
                            <ul>
                                <li>Phishing attacks targeting researchers</li>
                                <li>Social engineering attempts</li>
                                <li>Surveillance of diaspora communities</li>
                                <li>Malware targeting activists</li>
                            </ul>
                        </div>
                        <div class="guide-section">
                            <h4>📋 Best Practices</h4>
                            <ul>
                                <li>Document everything with timestamps</li>
                                <li>Store sensitive data encrypted (VeraCrypt)</li>
                                <li>Use secure communication (Signal)</li>
                                <li>Have a backup strategy</li>
                                <li>Know your legal protections</li>
                            </ul>
                        </div>
                        <div class="warning-box">⚠️ <strong>If Threatened:</strong> Contact Access Now Helpline (help@accessnow.org) or Committee to Protect Journalists (CPJ).</div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- MONITOR SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="monitor" class="section">
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">🐦</div><div><div class="card-title">Twitter/X Accounts</div><div class="card-subtitle">Track up to 10 accounts</div></div></div>
                    <div class="card-body">
                        <form id="addTwitterForm" style="margin-bottom:1rem;">
                            <div style="display:flex;gap:0.5rem;">
                                <input type="text" class="form-input" id="twitterUsername" placeholder="@username" style="flex:1;">
                                <button type="submit" class="btn btn-primary btn-sm">➕</button>
                            </div>
                            <input type="text" class="form-input" id="twitterDesc" placeholder="Description (optional)" style="margin-top:0.5rem;">
                        </form>
                        <div id="twitterResult"></div>
                        <div id="twitterList" class="scroll-box" style="max-height:300px;"></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">📰</div><div><div class="card-title">News Sources</div><div class="card-subtitle">Track up to 10 websites</div></div></div>
                    <div class="card-body">
                        <form id="addNewsForm" style="margin-bottom:1rem;">
                            <div style="display:flex;gap:0.5rem;">
                                <input type="text" class="form-input" id="newsName" placeholder="Source name" style="flex:1;">
                                <button type="submit" class="btn btn-primary btn-sm">➕</button>
                            </div>
                            <input type="url" class="form-input" id="newsUrl" placeholder="https://example.com" style="margin-top:0.5rem;">
                            <input type="text" class="form-input" id="newsDesc" placeholder="Description (optional)" style="margin-top:0.5rem;">
                        </form>
                        <div id="newsResult"></div>
                        <div id="newsList" class="scroll-box" style="max-height:300px;"></div>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top:1.5rem;">
                <div class="card-header"><div class="card-icon icon-purple">💡</div><div><div class="card-title">Suggested Sources</div></div></div>
                <div class="card-body">
                    <div class="grid-2">
                        <div>
                            <h4 style="color:var(--primary);margin-bottom:0.75rem;">🐦 Recommended Twitter Accounts</h4>
                            <div class="guide-section">
                                <ul>
                                    <li><strong>@IranIntl_En</strong> - Iran International (English)</li>
                                    <li><strong>@IranHrm</strong> - Iran Human Rights Monitor</li>
                                    <li><strong>@belaboratories</strong> - Bellingcat Labs</li>
                                    <li><strong>@NarimanGharib</strong> - OSINT researcher</li>
                                    <li><strong>@JasonMBrodsky</strong> - Iran policy expert</li>
                                    <li><strong>@Khaaastpp</strong> - Iran protest tracking</li>
                                </ul>
                            </div>
                        </div>
                        <div>
                            <h4 style="color:var(--primary);margin-bottom:0.75rem;">📰 Recommended News Sources</h4>
                            <div class="guide-section">
                                <ul>
                                    <li><strong>iranintl.com</strong> - Iran International</li>
                                    <li><strong>iranhr.net</strong> - Iran Human Rights</li>
                                    <li><strong>radiofarda.com</strong> - Radio Farda (RFE/RL)</li>
                                    <li><strong>bellingcat.com</strong> - Bellingcat</li>
                                    <li><strong>bbc.com/persian</strong> - BBC Persian</li>
                                    <li><strong>voanews.com/iran</strong> - VOA Iran</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- REFERENCES SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="references" class="section">
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-orange">📋</div><div><div class="card-title">Document Finding</div><div class="card-subtitle">Record investigation discoveries</div></div></div>
                    <div class="card-body">
                        <form id="addFindingForm">
                            <div class="form-group"><label class="form-label">Title *</label><input type="text" class="form-input" id="findingTitle" required placeholder="Brief description"></div>
                            <div class="form-group"><label class="form-label">Type</label><select class="form-input" id="findingType"><option value="">Select...</option><option value="LinkedIn">LinkedIn Connection</option><option value="Corporate">Corporate Link</option><option value="Sanctions">Sanctions Match</option><option value="Social Media">Social Media</option><option value="News">News Article</option><option value="Financial">Financial Connection</option><option value="Photo/Video">Photo/Video Evidence</option><option value="Other">Other</option></select></div>
                            <div class="form-group"><label class="form-label">Source URL</label><input type="url" class="form-input" id="findingUrl" placeholder="https://..."></div>
                            <div class="form-group"><label class="form-label">Source Name</label><input type="text" class="form-input" id="findingSource" placeholder="Website name"></div>
                            <div class="form-group"><label class="form-label">Importance</label><select class="form-input" id="findingImportance"><option value="Low">Low</option><option value="Medium" selected>Medium</option><option value="High">High</option><option value="Critical">Critical</option></select></div>
                            <div class="form-group"><label class="form-label">Description</label><textarea class="form-input" id="findingDesc" rows="3"></textarea></div>
                            <div class="form-group"><label class="form-label">Tags</label><input type="text" class="form-input" id="findingTags" placeholder="sanctions, corporate, IRGC"></div>
                            <button type="submit" class="btn btn-primary btn-block">📋 Add Finding</button>
                        </form>
                        <div id="findingResult" style="margin-top:1rem;"></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">📚</div><div><div class="card-title">Documented Findings</div></div></div>
                    <div class="card-body">
                        <div style="margin-bottom:1rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
                            <button class="btn btn-secondary btn-sm" onclick="loadFindings()">🔄 Refresh</button>
                            <select id="findingTypeFilter" class="form-input" style="width:auto;" onchange="loadFindings()">
                                <option value="">All Types</option>
                                <option value="LinkedIn">LinkedIn</option>
                                <option value="Corporate">Corporate</option>
                                <option value="Sanctions">Sanctions</option>
                                <option value="Financial">Financial</option>
                                <option value="Photo/Video">Photo/Video</option>
                            </select>
                        </div>
                        <div id="findingsList" class="scroll-box" style="max-height:500px;"></div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <!-- CONTACTS SECTION -->
        <!-- ═══════════════════════════════════════════════════════════════════════ -->
        <section id="contacts" class="section">
            <div class="alert alert-info" style="margin-bottom:1.5rem;">ℹ️ <strong>Important Resources:</strong> Organizations that can help with investigations, receive reports, provide legal support, or assist with security concerns.</div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-green">🕊️</div><div><div class="card-title">Human Rights Organizations</div></div></div>
                    <div class="card-body scroll-box">
                        <div class="contact-card"><div class="contact-name">Amnesty International - Iran</div><div class="contact-desc">Global human rights organization</div><div class="contact-links"><a href="mailto:iran@amnesty.org">📧 iran@amnesty.org</a><a href="https://www.amnesty.org/en/location/middle-east-and-north-africa/iran/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">Human Rights Watch - Iran</div><div class="contact-desc">Reports on human rights abuses</div><div class="contact-links"><a href="mailto:hrwpress@hrw.org">📧 hrwpress@hrw.org</a><a href="https://www.hrw.org/middle-east/n-africa/iran" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">Iran Human Rights (IHR)</div><div class="contact-desc">Norway-based documentation organization</div><div class="contact-links"><a href="mailto:info@iranhr.net">📧 info@iranhr.net</a><a href="https://iranhr.net/en/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">Center for Human Rights in Iran</div><div class="contact-desc">Independent research organization</div><div class="contact-links"><a href="mailto:info@iranhumanrights.org">📧 info@iranhumanrights.org</a><a href="https://iranhumanrights.org/" target="_blank">🔗 Website</a></div></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-blue">📰</div><div><div class="card-title">Investigative Journalism</div></div></div>
                    <div class="card-body scroll-box">
                        <div class="contact-card"><div class="contact-name">Bellingcat</div><div class="contact-desc">Open source investigations</div><div class="contact-links"><a href="mailto:contact@bellingcat.com">📧 contact@bellingcat.com</a><a href="https://www.bellingcat.com/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">OCCRP</div><div class="contact-desc">Investigative journalism network</div><div class="contact-links"><a href="mailto:info@occrp.org">📧 info@occrp.org</a><a href="https://www.occrp.org/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">Iran International</div><div class="contact-desc">London-based news network</div><div class="contact-links"><a href="mailto:info@iranintl.com">📧 info@iranintl.com</a><a href="https://www.iranintl.com/en" target="_blank">🔗 Website</a></div></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-red">🏛️</div><div><div class="card-title">Government Agencies</div></div></div>
                    <div class="card-body scroll-box">
                        <div class="contact-card"><div class="contact-name">OFAC (US Treasury)</div><div class="contact-desc">US sanctions enforcement</div><div class="contact-links"><a href="mailto:ofac_feedback@treasury.gov">📧 ofac_feedback@treasury.gov</a><a href="https://home.treasury.gov/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">FBI Tips</div><div class="contact-desc">Report foreign agents</div><div class="contact-links"><a href="https://tips.fbi.gov/" target="_blank">🔗 tips.fbi.gov</a></div></div>
                        <div class="contact-card"><div class="contact-name">UK OFSI</div><div class="contact-desc">UK sanctions office</div><div class="contact-links"><a href="mailto:ofsi@hmtreasury.gov.uk">📧 ofsi@hmtreasury.gov.uk</a></div></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header"><div class="card-icon icon-purple">🛡️</div><div><div class="card-title">Digital Security & Legal</div></div></div>
                    <div class="card-body scroll-box">
                        <div class="contact-card" style="border:1px solid var(--danger);"><div class="contact-name">🚨 Access Now Helpline</div><div class="contact-desc">24/7 digital security assistance</div><div class="contact-links"><a href="mailto:help@accessnow.org">📧 help@accessnow.org</a><a href="https://www.accessnow.org/help/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">Committee to Protect Journalists</div><div class="contact-desc">Journalist safety resources</div><div class="contact-links"><a href="mailto:info@cpj.org">📧 info@cpj.org</a><a href="https://cpj.org/" target="_blank">🔗 Website</a></div></div>
                        <div class="contact-card"><div class="contact-name">EFF</div><div class="contact-desc">Digital rights legal advocacy</div><div class="contact-links"><a href="mailto:info@eff.org">📧 info@eff.org</a><a href="https://www.eff.org/" target="_blank">🔗 Website</a></div></div>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top:1.5rem;">
                <div class="card-header"><div class="card-icon icon-orange">➕</div><div><div class="card-title">Add Your Own Contact</div></div></div>
                <div class="card-body">
                    <div class="grid-2">
                        <form id="addContactForm">
                            <div class="form-group"><label class="form-label">Name *</label><input type="text" class="form-input" id="contactName" required placeholder="Contact name"></div>
                            <div class="form-group"><label class="form-label">Type</label><select class="form-input" id="contactType"><option value="">Select...</option><option value="Human Rights">Human Rights</option><option value="Journalism">Journalism</option><option value="Government">Government</option><option value="Legal">Legal</option><option value="Personal">Personal</option></select></div>
                            <div class="form-group"><label class="form-label">Email</label><input type="email" class="form-input" id="contactEmail" placeholder="email@example.com"></div>
                            <div class="form-group"><label class="form-label">Website</label><input type="url" class="form-input" id="contactUrl" placeholder="https://..."></div>
                            <div class="form-group"><label class="form-label">Description</label><textarea class="form-input" id="contactDesc" rows="2"></textarea></div>
                            <button type="submit" class="btn btn-primary">➕ Add Contact</button>
                        </form>
                        <div>
                            <h4 style="color:var(--primary);margin-bottom:1rem;">Your Saved Contacts</h4>
                            <div id="userContactsList"></div>
                        </div>
                    </div>
                    <div id="contactResult" style="margin-top:1rem;"></div>
                </div>
            </div>
        </section>
    </main>
    
    <!-- Subject Detail Modal -->
    <div id="subjectModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Subject Details</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="subjectModalBody"></div>
        </div>
    </div>
    
    <footer class="footer">
        <p><strong>Iran OSINT Tracker v3.0</strong> — Complete Open Source Intelligence Platform</p>
        <p style="margin-top:0.5rem;">All methods comply with platform Terms of Service. Based on Berkeley Protocol for digital evidence.</p>
        <p style="margin-top:0.5rem;font-size:0.8rem;">For journalism, research, and human rights documentation. Use responsibly.</p>
    </footer>
    
    <script>
        // ═══════════════════════════════════════════════════════════════════════════
        // FIXED: Navigation - properly receives the button element as parameter
        // ═══════════════════════════════════════════════════════════════════════════
        function showSection(id, btn) {
            // Remove active class from all sections and buttons
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            
            // Activate the selected section
            document.getElementById(id).classList.add('active');
            
            // Activate the clicked button
            if (btn) {
                btn.classList.add('active');
            }
            
            // Load data for specific sections
            if (id === 'subjects') loadSubjects();
            if (id === 'monitor') { loadTwitterAccounts(); loadNewsSources(); }
            if (id === 'references') loadFindings();
            if (id === 'contacts') loadUserContacts();
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // FIXED: API helper with proper error handling
        // ═══════════════════════════════════════════════════════════════════════════
        async function api(endpoint, method = 'GET', data = null) {
            try {
                const opts = { method, headers: { 'Content-Type': 'application/json' } };
                if (data) opts.body = JSON.stringify(data);
                const r = await fetch('/api/' + endpoint, opts);
                if (!r.ok) {
                    console.error('API error:', r.status, r.statusText);
                    return { status: 'error', message: 'Server error: ' + r.status };
                }
                return await r.json();
            } catch (err) {
                console.error('API call failed:', err);
                return { status: 'error', message: err.message };
            }
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Utility: HTML escaping to prevent XSS
        // ═══════════════════════════════════════════════════════════════════════════
        function escapeHtml(text) {
            if (text === null || text === undefined) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Subjects functionality
        // ═══════════════════════════════════════════════════════════════════════════
        document.getElementById('addSubjectForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = { 
                name_en: document.getElementById('nameEn').value, 
                name_fa: document.getElementById('nameFa').value, 
                location: document.getElementById('location').value, 
                event: document.getElementById('event').value, 
                notes: document.getElementById('notes').value 
            };
            const r = await api('subjects', 'POST', data);
            const resultEl = document.getElementById('addResult');
            if (r.status === 'success') {
                resultEl.innerHTML = '<div class="alert alert-success">✅ Subject added (ID: ' + r.id + ')</div>';
                document.getElementById('addSubjectForm').reset();
                loadStats();
            } else {
                resultEl.innerHTML = '<div class="alert alert-error">❌ Error: ' + (r.message || 'Unknown error') + '</div>';
            }
            setTimeout(() => resultEl.innerHTML = '', 5000);
        });
        
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('searchName').value;
            const nameFa = document.getElementById('searchNameFa').value;
            let url = 'search?name=' + encodeURIComponent(name);
            if (nameFa) url += '&name_fa=' + encodeURIComponent(nameFa);
            const r = await api(url);
            
            if (r.status === 'error') {
                alert('Error: ' + r.message);
                return;
            }
            
            document.getElementById('searchResultsContainer').style.display = 'block';
            document.getElementById('searchResultsFor').textContent = 'For: ' + name;
            let html = '';
            for (const [cat, links] of Object.entries(r)) {
                html += '<div class="search-category"><h4>' + cat.replace(/_/g, ' ') + '</h4>';
                for (const [n, u] of Object.entries(links)) {
                    html += '<a href="' + u + '" target="_blank" class="search-link">' + n.replace(/_/g, ' ') + '</a>';
                }
                html += '</div>';
            }
            document.getElementById('searchResults').innerHTML = html;
        });
        
        async function loadSubjects() {
            const status = document.getElementById('statusFilter')?.value || '';
            let url = 'subjects';
            if (status) url += '?status=' + status;
            const subjects = await api(url);
            
            if (Array.isArray(subjects) && subjects.length > 0) {
                document.getElementById('subjectsTable').innerHTML = subjects.map(s => 
                    '<tr>' +
                    '<td>' + s.id + '</td>' +
                    '<td><strong>' + escapeHtml(s.name_en) + '</strong>' + 
                        (s.name_fa ? '<br><span style="color:var(--gray)">' + escapeHtml(s.name_fa) + '</span>' : '') + 
                    '</td>' +
                    '<td>' + escapeHtml(s.location_spotted || '-') + '</td>' +
                    '<td><span class="badge badge-' + (s.status || 'new').toLowerCase() + '">' + (s.status || 'New') + '</span></td>' +
                    '<td><span class="badge badge-' + (s.risk_level || 'unknown').toLowerCase() + '">' + (s.risk_level || 'Unknown') + '</span></td>' +
                    '<td><button class="btn btn-secondary btn-sm" onclick="viewSubject(' + s.id + ')">View</button></td>' +
                    '</tr>'
                ).join('');
            } else {
                document.getElementById('subjectsTable').innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--gray)">No subjects found</td></tr>';
            }
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // FIXED: viewSubject - proper string escaping for modal content
        // ═══════════════════════════════════════════════════════════════════════════
        async function viewSubject(id) {
            const s = await api('subjects/' + id);
            if (!s || s.error) {
                alert('Subject not found');
                return;
            }
            
            // Build the modal HTML with proper escaping
            const nameEn = escapeHtml(s.name_en || '');
            const nameFa = s.name_fa ? ' (' + escapeHtml(s.name_fa) + ')' : '';
            const location = escapeHtml(s.location_spotted || '-');
            const notes = escapeHtml(s.notes || '');
            
            const html = `
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <p><strong>${nameEn}</strong>${nameFa}</p>
                </div>
                <div class="form-group">
                    <label class="form-label">Location</label>
                    <p>${location}</p>
                </div>
                <div class="form-group">
                    <label class="form-label">Status</label>
                    <select class="form-input" id="modalStatus" onchange="updateSubjectField(${s.id}, 'status', this.value)">
                        <option ${s.status === 'New' ? 'selected' : ''}>New</option>
                        <option ${s.status === 'Investigating' ? 'selected' : ''}>Investigating</option>
                        <option ${s.status === 'Verified' ? 'selected' : ''}>Verified</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Risk Level</label>
                    <select class="form-input" id="modalRisk" onchange="updateSubjectField(${s.id}, 'risk_level', this.value)">
                        <option ${s.risk_level === 'Unknown' ? 'selected' : ''}>Unknown</option>
                        <option ${s.risk_level === 'Low' ? 'selected' : ''}>Low</option>
                        <option ${s.risk_level === 'Medium' ? 'selected' : ''}>Medium</option>
                        <option ${s.risk_level === 'High' ? 'selected' : ''}>High</option>
                        <option ${s.risk_level === 'Critical' ? 'selected' : ''}>Critical</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input" id="modalNotes" rows="3" onchange="updateSubjectField(${s.id}, 'notes', this.value)">${notes}</textarea>
                </div>
                <button class="btn btn-danger" onclick="deleteSubject(${s.id})">🗑️ Delete</button>
            `;
            
            document.getElementById('subjectModalBody').innerHTML = html;
            document.getElementById('subjectModal').classList.add('active');
        }
        
        async function updateSubjectField(id, field, value) {
            const data = {};
            data[field] = value;
            await api('subjects/' + id, 'PUT', data);
        }
        
        async function deleteSubject(id) { 
            if (confirm('Are you sure you want to delete this subject?')) { 
                await api('subjects/' + id, 'DELETE'); 
                closeModal(); 
                loadSubjects(); 
                loadStats(); 
            } 
        }
        
        function closeModal() { 
            document.getElementById('subjectModal').classList.remove('active'); 
        }
        
        // Close modal when clicking outside
        document.getElementById('subjectModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
        
        async function loadStats() {
            const r = await api('stats');
            if (r && !r.error) {
                document.getElementById('statTotal').textContent = r.total || 0;
                document.getElementById('statNew').textContent = r.by_status?.New || 0;
                document.getElementById('statInvestigating').textContent = r.by_status?.Investigating || 0;
                document.getElementById('statVerified').textContent = r.by_status?.Verified || 0;
            }
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Monitor - Twitter
        // ═══════════════════════════════════════════════════════════════════════════
        document.getElementById('addTwitterForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const r = await api('monitor/twitter', 'POST', { 
                username: document.getElementById('twitterUsername').value, 
                description: document.getElementById('twitterDesc').value 
            });
            const resultEl = document.getElementById('twitterResult');
            if (r.status === 'success') {
                resultEl.innerHTML = '<div class="alert alert-success">✅ Added</div>';
                document.getElementById('addTwitterForm').reset();
                loadTwitterAccounts();
            } else {
                resultEl.innerHTML = '<div class="alert alert-error">❌ ' + (r.message || 'Error') + '</div>';
            }
            setTimeout(() => resultEl.innerHTML = '', 5000);
        });
        
        async function loadTwitterAccounts() {
            const accounts = await api('monitor/twitter');
            if (Array.isArray(accounts) && accounts.length > 0) {
                document.getElementById('twitterList').innerHTML = accounts.map(a => 
                    '<div class="monitor-item">' +
                    '<div><div class="monitor-item-name">@' + escapeHtml(a.username) + '</div>' +
                    '<div class="monitor-item-desc">' + escapeHtml(a.description || '') + '</div></div>' +
                    '<div style="display:flex;gap:0.5rem;">' +
                    '<a href="https://twitter.com/' + encodeURIComponent(a.username) + '" target="_blank" class="btn btn-secondary btn-sm">Open</a>' +
                    '<button class="btn btn-danger btn-sm" onclick="deleteTwitter(' + a.id + ')">×</button>' +
                    '</div></div>'
                ).join('');
            } else {
                document.getElementById('twitterList').innerHTML = '<div class="empty-state">No accounts added yet</div>';
            }
        }
        
        async function deleteTwitter(id) { 
            await api('monitor/twitter/' + id, 'DELETE'); 
            loadTwitterAccounts(); 
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Monitor - News
        // ═══════════════════════════════════════════════════════════════════════════
        document.getElementById('addNewsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const r = await api('monitor/news', 'POST', { 
                name: document.getElementById('newsName').value, 
                url: document.getElementById('newsUrl').value, 
                description: document.getElementById('newsDesc').value 
            });
            const resultEl = document.getElementById('newsResult');
            if (r.status === 'success') {
                resultEl.innerHTML = '<div class="alert alert-success">✅ Added</div>';
                document.getElementById('addNewsForm').reset();
                loadNewsSources();
            } else {
                resultEl.innerHTML = '<div class="alert alert-error">❌ ' + (r.message || 'Error') + '</div>';
            }
            setTimeout(() => resultEl.innerHTML = '', 5000);
        });
        
        async function loadNewsSources() {
            const sources = await api('monitor/news');
            if (Array.isArray(sources) && sources.length > 0) {
                document.getElementById('newsList').innerHTML = sources.map(s => 
                    '<div class="monitor-item">' +
                    '<div><div class="monitor-item-name">' + escapeHtml(s.name) + '</div>' +
                    '<div class="monitor-item-desc">' + escapeHtml(s.description || s.url) + '</div></div>' +
                    '<div style="display:flex;gap:0.5rem;">' +
                    '<a href="' + escapeHtml(s.url) + '" target="_blank" class="btn btn-secondary btn-sm">Open</a>' +
                    '<button class="btn btn-danger btn-sm" onclick="deleteNews(' + s.id + ')">×</button>' +
                    '</div></div>'
                ).join('');
            } else {
                document.getElementById('newsList').innerHTML = '<div class="empty-state">No sources added yet</div>';
            }
        }
        
        async function deleteNews(id) { 
            await api('monitor/news/' + id, 'DELETE'); 
            loadNewsSources(); 
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Findings
        // ═══════════════════════════════════════════════════════════════════════════
        document.getElementById('addFindingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = { 
                title: document.getElementById('findingTitle').value, 
                finding_type: document.getElementById('findingType').value, 
                source_url: document.getElementById('findingUrl').value, 
                source_name: document.getElementById('findingSource').value, 
                importance: document.getElementById('findingImportance').value, 
                description: document.getElementById('findingDesc').value, 
                tags: document.getElementById('findingTags').value 
            };
            const r = await api('findings', 'POST', data);
            const resultEl = document.getElementById('findingResult');
            if (r.status === 'success') {
                resultEl.innerHTML = '<div class="alert alert-success">✅ Finding added</div>';
                document.getElementById('addFindingForm').reset();
                loadFindings();
            } else {
                resultEl.innerHTML = '<div class="alert alert-error">❌ Error</div>';
            }
            setTimeout(() => resultEl.innerHTML = '', 5000);
        });
        
        async function loadFindings() {
            const type = document.getElementById('findingTypeFilter')?.value || '';
            let url = 'findings';
            if (type) url += '?finding_type=' + encodeURIComponent(type);
            const findings = await api(url);
            
            if (Array.isArray(findings) && findings.length > 0) {
                document.getElementById('findingsList').innerHTML = findings.map(f => 
                    '<div class="finding-card">' +
                    '<div class="finding-title">' + escapeHtml(f.title) + 
                    ' <span class="badge badge-' + (f.importance || 'medium').toLowerCase() + '">' + (f.importance || 'Medium') + '</span></div>' +
                    '<div class="finding-meta">' + escapeHtml(f.finding_type || '') + ' • ' + escapeHtml(f.source_name || '') + 
                    (f.verified ? ' • ✅ Verified' : '') + '</div>' +
                    '<div>' + escapeHtml(f.description || '') + '</div>' +
                    '<div style="margin-top:0.5rem;">' + 
                    (f.source_url ? '<a href="' + escapeHtml(f.source_url) + '" target="_blank" class="btn btn-secondary btn-sm">Source</a> ' : '') + 
                    '<button class="btn btn-danger btn-sm" onclick="deleteFinding(' + f.id + ')">Delete</button>' +
                    '</div></div>'
                ).join('');
            } else {
                document.getElementById('findingsList').innerHTML = '<div class="empty-state">No findings documented yet</div>';
            }
        }
        
        async function deleteFinding(id) { 
            if (confirm('Delete this finding?')) { 
                await api('findings/' + id, 'DELETE'); 
                loadFindings(); 
            } 
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Contacts
        // ═══════════════════════════════════════════════════════════════════════════
        document.getElementById('addContactForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = { 
                name: document.getElementById('contactName').value, 
                contact_type: document.getElementById('contactType').value, 
                email: document.getElementById('contactEmail').value, 
                url: document.getElementById('contactUrl').value, 
                description: document.getElementById('contactDesc').value 
            };
            const r = await api('contacts', 'POST', data);
            const resultEl = document.getElementById('contactResult');
            if (r.status === 'success') {
                resultEl.innerHTML = '<div class="alert alert-success">✅ Contact added</div>';
                document.getElementById('addContactForm').reset();
                loadUserContacts();
            } else {
                resultEl.innerHTML = '<div class="alert alert-error">❌ Error</div>';
            }
            setTimeout(() => resultEl.innerHTML = '', 5000);
        });
        
        async function loadUserContacts() {
            const contacts = await api('contacts/user');
            if (Array.isArray(contacts) && contacts.length > 0) {
                document.getElementById('userContactsList').innerHTML = contacts.map(c => 
                    '<div class="contact-card">' +
                    '<div class="contact-name">' + escapeHtml(c.name) + '</div>' +
                    '<div class="contact-desc">' + escapeHtml(c.description || c.contact_type || '') + '</div>' +
                    '<div class="contact-links">' + 
                    (c.email ? '<a href="mailto:' + escapeHtml(c.email) + '">📧 ' + escapeHtml(c.email) + '</a>' : '') + 
                    (c.url ? '<a href="' + escapeHtml(c.url) + '" target="_blank">🔗 Website</a>' : '') + 
                    '<button class="btn btn-danger btn-sm" onclick="deleteContact(' + c.id + ')">Delete</button>' +
                    '</div></div>'
                ).join('');
            } else {
                document.getElementById('userContactsList').innerHTML = '<div class="empty-state">No saved contacts</div>';
            }
        }
        
        async function deleteContact(id) { 
            await api('contacts/' + id, 'DELETE'); 
            loadUserContacts(); 
        }
        
        // ═══════════════════════════════════════════════════════════════════════════
        // Initialize on page load
        // ═══════════════════════════════════════════════════════════════════════════
        loadStats();
    </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════════════════════════════════

class RequestHandler(BaseHTTPRequestHandler):
    db: Database = None
    subjects: SubjectManager = None
    monitor: MonitorManager = None
    findings: FindingsManager = None
    contacts: ContactsManager = None
    search_gen: SearchGenerator = None
    config: Config = None
    
    def log_message(self, format, *args): 
        pass  # Suppress default logging
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path in ['/', '/index.html']:
            self.send_html(generate_dashboard_html(self.config))
        
        elif path == '/api/subjects':
            status = params.get('status', [None])[0]
            risk = params.get('risk_level', [None])[0]
            self.send_json(self.subjects.get_all(status=status, risk_level=risk))
        
        elif path.startswith('/api/subjects/'):
            try:
                sid = int(path.split('/')[-1])
                self.send_json(self.subjects.get(sid) or {"error": "Not found"})
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif path == '/api/search':
            name = params.get('name', [''])[0]
            name_fa = params.get('name_fa', [''])[0]
            if name:
                self.send_json(self.search_gen.generate_all(name, name_fa))
            else:
                self.send_json({"error": "Name required"}, 400)
        
        elif path == '/api/stats':
            self.send_json(self.subjects.get_statistics())
        
        elif path == '/api/monitor/twitter':
            self.send_json(self.monitor.get_twitter())
        
        elif path == '/api/monitor/news':
            self.send_json(self.monitor.get_news())
        
        elif path == '/api/findings':
            ftype = params.get('finding_type', [None])[0]
            importance = params.get('importance', [None])[0]
            self.send_json(self.findings.get_all(finding_type=ftype, importance=importance))
        
        elif path.startswith('/api/findings/'):
            try:
                fid = int(path.split('/')[-1])
                self.send_json(self.findings.get(fid) or {"error": "Not found"})
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif path == '/api/contacts/user':
            self.send_json(self.contacts.get_user())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(content_length)) if content_length else {}
        
        if self.path == '/api/subjects':
            self.send_json(self.subjects.add(
                name_en=data.get('name_en', ''),
                name_fa=data.get('name_fa', ''),
                location=data.get('location', ''),
                event=data.get('event', ''),
                notes=data.get('notes', '')
            ))
        
        elif self.path == '/api/monitor/twitter':
            self.send_json(self.monitor.add_twitter(
                username=data.get('username', ''),
                description=data.get('description', '')
            ))
        
        elif self.path == '/api/monitor/news':
            self.send_json(self.monitor.add_news(
                name=data.get('name', ''),
                url=data.get('url', ''),
                description=data.get('description', '')
            ))
        
        elif self.path == '/api/findings':
            self.send_json(self.findings.add(
                title=data.get('title', ''),
                finding_type=data.get('finding_type', ''),
                description=data.get('description', ''),
                source_url=data.get('source_url', ''),
                source_name=data.get('source_name', ''),
                tags=data.get('tags', ''),
                importance=data.get('importance', 'Medium')
            ))
        
        elif self.path == '/api/contacts':
            self.send_json(self.contacts.add(
                name=data.get('name', ''),
                contact_type=data.get('contact_type', ''),
                email=data.get('email', ''),
                url=data.get('url', ''),
                description=data.get('description', '')
            ))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_PUT(self):
        if self.path.startswith('/api/subjects/'):
            try:
                sid = int(self.path.split('/')[-1])
                content_length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(content_length)) if content_length else {}
                self.send_json(self.subjects.update(sid, **data))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_DELETE(self):
        if self.path.startswith('/api/subjects/'):
            try:
                sid = int(self.path.split('/')[-1])
                self.send_json(self.subjects.delete(sid))
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif self.path.startswith('/api/monitor/twitter/'):
            try:
                aid = int(self.path.split('/')[-1])
                self.send_json(self.monitor.delete_twitter(aid))
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif self.path.startswith('/api/monitor/news/'):
            try:
                sid = int(self.path.split('/')[-1])
                self.send_json(self.monitor.delete_news(sid))
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif self.path.startswith('/api/findings/'):
            try:
                fid = int(self.path.split('/')[-1])
                self.send_json(self.findings.delete(fid))
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        elif self.path.startswith('/api/contacts/'):
            try:
                cid = int(self.path.split('/')[-1])
                self.send_json(self.contacts.delete(cid))
            except: 
                self.send_json({"error": "Invalid ID"}, 400)
        
        else:
            self.send_response(404)
            self.end_headers()


def run_server(config: Config, port: int = 8000):
    """Start the OSINT Tracker web server"""
    db = Database(config.DB_PATH)
    
    # Initialize handlers
    RequestHandler.db = db
    RequestHandler.subjects = SubjectManager(db, config)
    RequestHandler.monitor = MonitorManager(db)
    RequestHandler.findings = FindingsManager(db)
    RequestHandler.contacts = ContactsManager(db, config)
    RequestHandler.search_gen = SearchGenerator(config)
    RequestHandler.config = config
    
    # Find available port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
            break
        except OSError:
            port += 1
    
    server = HTTPServer(('', port), RequestHandler)
    url = f"http://localhost:{port}"
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🔍 Iran OSINT Tracker v3.0 - Complete Edition                               ║
║                                                                               ║
║   Dashboard: {url:<58} ║
║                                                                               ║
║   NEW FEATURES:                                                               ║
║   • 💰 Follow the Money - Financial investigation tools                       ║
║   • 📷 Photo/Video Verification - Media forensics                             ║
║   • 🌐 Internet Status - Iran connectivity monitoring                         ║
║   • 📚 Enhanced database resources                                            ║
║                                                                               ║
║   Press Ctrl+C to stop                                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✔ Server stopped")
        server.shutdown()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🔍 Iran OSINT Tracker v3.0 - Complete Edition")
    parser.add_argument("--dashboard", action="store_true", help="Launch web dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Dashboard port")
    parser.add_argument("--search", metavar="NAME", help="Generate search URLs")
    parser.add_argument("--add", metavar="NAME", help="Add investigation subject")
    parser.add_argument("--list", action="store_true", help="List all subjects")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    config = Config()
    
    if args.dashboard:
        run_server(config, args.port)
    
    elif args.search:
        search_gen = SearchGenerator(config)
        urls = search_gen.generate_all(args.search)
        print(f"\n🔎 Search URLs for: {args.search}\n")
        for category, links in urls.items():
            print(f"\n📂 {category.upper()}")
            for name, url in links.items():
                print(f"   • {name}: {url}")
    
    elif args.add:
        db = Database(config.DB_PATH)
        subjects = SubjectManager(db, config)
        result = subjects.add(name_en=args.add)
        print(f"\n✅ Subject added: ID {result['id']}")
    
    elif args.list:
        db = Database(config.DB_PATH)
        subjects = SubjectManager(db, config)
        all_subjects = subjects.get_all()
        print(f"\n📋 Subjects ({len(all_subjects)} total)\n")
        for s in all_subjects:
            print(f"  [{s['id']}] {s['name_en']} - {s['status']} ({s['risk_level']})")
    
    elif args.stats:
        db = Database(config.DB_PATH)
        subjects = SubjectManager(db, config)
        stats = subjects.get_statistics()
        print(f"\n📊 Statistics")
        print(f"   Total: {stats['total']}")
        print(f"   By Status: {stats['by_status']}")
        print(f"   By Risk: {stats['by_risk']}")
    
    else:
        parser.print_help()
        print("\n\n🔍 Quick start: python iran_osint_v3_complete.py --dashboard")


if __name__ == "__main__":
    main()
