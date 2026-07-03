from django.core.management.base import BaseCommand

from apps.web_security.models import RateLimitRule, SecuritySettings, ThreatPattern


class Command(BaseCommand):
    """Seed default threat patterns and rate limit rules."""

    help = "Seed default threat patterns and rate limit rules for web security"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be created without making changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing patterns with same name",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Ensure SecuritySettings exists
        if not dry_run:
            SecuritySettings.get_settings()
            self.stdout.write(self.style.SUCCESS("SecuritySettings initialized"))

        # Seed threat patterns
        patterns_created = self._seed_threat_patterns(dry_run, force)

        # Seed rate limit rules
        rules_created = self._seed_rate_limit_rules(dry_run, force)

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Patterns: {patterns_created} created | Rules: {rules_created} created"))

    def _seed_threat_patterns(self, dry_run, force):
        """Seed default threat detection patterns."""
        self.stdout.write("\n--- Threat Patterns ---")

        patterns = [
            # WordPress patterns
            {
                "name": "WordPress Login",
                "description": "Detects WordPress login page access attempts",
                "pattern": r"wp-login\.php",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.WORDPRESS,
                "threat_level": ThreatPattern.ThreatLevel.MEDIUM,
                "threat_score": 20,
            },
            {
                "name": "WordPress Admin",
                "description": "Detects WordPress admin panel access attempts",
                "pattern": r"wp-admin",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.WORDPRESS,
                "threat_level": ThreatPattern.ThreatLevel.MEDIUM,
                "threat_score": 25,
            },
            {
                "name": "WordPress Content",
                "description": "Detects WordPress content directory access",
                "pattern": r"wp-content",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.WORDPRESS,
                "threat_level": ThreatPattern.ThreatLevel.LOW,
                "threat_score": 15,
            },
            {
                "name": "WordPress Includes",
                "description": "Detects WordPress includes directory access",
                "pattern": r"wp-includes",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.WORDPRESS,
                "threat_level": ThreatPattern.ThreatLevel.LOW,
                "threat_score": 15,
            },
            {
                "name": "XMLRPC",
                "description": "Detects XML-RPC endpoint access (common attack vector)",
                "pattern": r"xmlrpc\.php",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.WORDPRESS,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            # PHP patterns
            {
                "name": "PHP Files",
                "description": "Detects access attempts to PHP files",
                "pattern": r"\.php($|\?)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.PHP,
                "threat_level": ThreatPattern.ThreatLevel.MEDIUM,
                "threat_score": 20,
            },
            {
                "name": "PHPInfo",
                "description": "Detects phpinfo page access attempts",
                "pattern": r"phpinfo",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.PHP,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            # Sensitive files
            {
                "name": "Environment Files",
                "description": "Detects access to .env files",
                "pattern": r"\.env",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SENSITIVE,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
            },
            {
                "name": "Git Directory",
                "description": "Detects access to .git directory",
                "pattern": r"\.git",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SENSITIVE,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
            },
            {
                "name": "Backup Files",
                "description": "Detects access to backup files",
                "pattern": r"\.(bak|backup|old|orig|save|swp|tmp)($|\?)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SENSITIVE,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            {
                "name": "Config Files",
                "description": "Detects access to configuration files",
                "pattern": r"(config|settings|database)\.(yml|yaml|json|xml|ini)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SENSITIVE,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 35,
            },
            # Admin panels
            {
                "name": "PHPMyAdmin",
                "description": "Detects PHPMyAdmin access attempts",
                "pattern": r"(phpmyadmin|pma|myadmin|mysql)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.ADMIN,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            {
                "name": "Adminer",
                "description": "Detects Adminer access attempts",
                "pattern": r"adminer",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.ADMIN,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            # Vulnerability scanners
            {
                "name": "Nikto Scanner",
                "description": "Detects Nikto vulnerability scanner",
                "pattern": r"nikto",
                "match_type": ThreatPattern.MatchType.USER_AGENT,
                "category": ThreatPattern.Category.SCANNER,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 35,
            },
            {
                "name": "SQLMap Scanner",
                "description": "Detects SQLMap tool",
                "pattern": r"sqlmap",
                "match_type": ThreatPattern.MatchType.USER_AGENT,
                "category": ThreatPattern.Category.SCANNER,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
            },
            {
                "name": "Nmap Scanner",
                "description": "Detects Nmap scanner",
                "pattern": r"nmap",
                "match_type": ThreatPattern.MatchType.USER_AGENT,
                "category": ThreatPattern.Category.SCANNER,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            {
                "name": "Acunetix Scanner",
                "description": "Detects Acunetix vulnerability scanner",
                "pattern": r"acunetix",
                "match_type": ThreatPattern.MatchType.USER_AGENT,
                "category": ThreatPattern.Category.SCANNER,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 35,
            },
            # SQL Injection
            {
                "name": "SQL UNION Injection",
                "description": "Detects SQL UNION-based injection attempts",
                "pattern": r"union\s+(?:all\s+)?select",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.INJECTION,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
                "case_sensitive": False,
            },
            {
                "name": "SQL OR Injection",
                "description": "Detects SQL OR-based injection attempts",
                "pattern": r"[\s'\"]+or\s+1\s*=\s*1",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.INJECTION,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
                "case_sensitive": False,
            },
            {
                "name": "SQL Comment Injection",
                "description": "Detects SQL comment-based injection",
                "pattern": r"(--\s|--$|/\*|;--)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.INJECTION,
                "threat_level": ThreatPattern.ThreatLevel.HIGH,
                "threat_score": 30,
            },
            # Path traversal
            {
                "name": "Directory Traversal",
                "description": "Detects directory traversal attempts (../ or ..\\). Uses negative lookbehind to avoid matching ellipsis (.../) from old system URLs.",
                "pattern": r"(^|[^.])\.\./|(^|[^.])\.\.\\",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.TRAVERSAL,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
            },
            {
                "name": "URL Encoded Traversal",
                "description": "Detects URL-encoded directory traversal",
                "pattern": r"%2e%2e(%2f|%5c)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.TRAVERSAL,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
                "case_sensitive": False,
            },
            # Webshells
            {
                "name": "Common Webshells",
                "description": "Detects access to known webshell names",
                "pattern": r"(c99|r57|wso|b374k|webshell)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SHELL,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
                "case_sensitive": False,
            },
            {
                "name": "Shell Commands in Path",
                "description": "Detects shell command patterns in URL",
                "pattern": r"(cmd=|exec=|shell=|command=)",
                "match_type": ThreatPattern.MatchType.PATH,
                "category": ThreatPattern.Category.SHELL,
                "threat_level": ThreatPattern.ThreatLevel.CRITICAL,
                "threat_score": 40,
                "case_sensitive": False,
            },
        ]

        created = 0
        for pattern_data in patterns:
            name = pattern_data["name"]

            if dry_run:
                self.stdout.write(f"  Would create: {name}")
                created += 1
                continue

            existing = ThreatPattern.objects.filter(name=name).first()
            if existing:
                if force:
                    for key, value in pattern_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    self.stdout.write(f"  Updated: {name}")
                    created += 1
                else:
                    self.stdout.write(f"  Skipped (exists): {name}")
            else:
                ThreatPattern.objects.create(**pattern_data)
                self.stdout.write(self.style.SUCCESS(f"  Created: {name}"))
                created += 1

        return created

    def _seed_rate_limit_rules(self, dry_run, force):
        """Seed default rate limit rules."""
        self.stdout.write("\n--- Rate Limit Rules ---")

        rules = [
            {
                "name": "Login Rate Limit",
                "description": "Prevent brute force login attempts",
                "path_pattern": "*/login*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 10,
                "time_window_seconds": 60,
                "action": RateLimitRule.Action.BLOCK,
                "block_duration_minutes": 5,
                "priority": 10,
            },
            {
                "name": "Registration Rate Limit",
                "description": "Prevent registration spam",
                "path_pattern": "*/register*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 5,
                "time_window_seconds": 300,
                "action": RateLimitRule.Action.BLOCK,
                "block_duration_minutes": 10,
                "priority": 10,
            },
            {
                "name": "Password Reset Rate Limit",
                "description": "Prevent password reset abuse",
                "path_pattern": "*/password*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 5,
                "time_window_seconds": 300,
                "action": RateLimitRule.Action.BLOCK,
                "block_duration_minutes": 10,
                "priority": 10,
            },
            {
                "name": "API Rate Limit",
                "description": "General API rate limiting",
                "path_pattern": "/api/*",
                "http_method": RateLimitRule.HttpMethod.ALL,
                "max_requests": 100,
                "time_window_seconds": 60,
                "action": RateLimitRule.Action.THROTTLE,
                "block_duration_minutes": 1,
                "priority": 50,
            },
            {
                "name": "Search Rate Limit",
                "description": "Prevent search abuse",
                "path_pattern": "*/search*",
                "http_method": RateLimitRule.HttpMethod.ALL,
                "max_requests": 30,
                "time_window_seconds": 60,
                "action": RateLimitRule.Action.THROTTLE,
                "block_duration_minutes": 1,
                "priority": 30,
            },
            {
                "name": "File Upload Rate Limit",
                "description": "Limit file uploads",
                "path_pattern": "*/upload*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 10,
                "time_window_seconds": 60,
                "action": RateLimitRule.Action.BLOCK,
                "block_duration_minutes": 5,
                "priority": 20,
            },
            {
                "name": "Contact Form Rate Limit",
                "description": "Prevent contact form spam",
                "path_pattern": "*/contact*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 5,
                "time_window_seconds": 300,
                "action": RateLimitRule.Action.BLOCK,
                "block_duration_minutes": 10,
                "priority": 20,
            },
            {
                "name": "General POST Rate Limit",
                "description": "General rate limit for all POST requests",
                "path_pattern": "*",
                "http_method": RateLimitRule.HttpMethod.POST,
                "max_requests": 60,
                "time_window_seconds": 60,
                "action": RateLimitRule.Action.THROTTLE,
                "block_duration_minutes": 1,
                "priority": 100,
            },
        ]

        created = 0
        for rule_data in rules:
            name = rule_data["name"]

            if dry_run:
                self.stdout.write(f"  Would create: {name}")
                created += 1
                continue

            existing = RateLimitRule.objects.filter(name=name).first()
            if existing:
                if force:
                    for key, value in rule_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    self.stdout.write(f"  Updated: {name}")
                    created += 1
                else:
                    self.stdout.write(f"  Skipped (exists): {name}")
            else:
                RateLimitRule.objects.create(**rule_data)
                self.stdout.write(self.style.SUCCESS(f"  Created: {name}"))
                created += 1

        return created
