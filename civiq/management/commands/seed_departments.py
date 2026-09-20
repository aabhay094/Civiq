"""
Run this anytime with:

    python manage.py seed_departments

Populates (or re-confirms) the 5 real Lucknow departments and 13 grievance
categories with their public official contact emails. Safe to run multiple
times — uses get_or_create, so it will never create duplicates.

Use this if the data migration (0002_seed_data.py) didn't apply for any
reason, or if you just want to double check what's actually in your
database right now.
"""

from django.core.management.base import BaseCommand

from civiq.models import Department, Sector

DEPARTMENTS = [
    {
        "name": "Nagar Nigam Lucknow (Roads & Sanitation)",
        "slug": "nagar-nigam-lucknow",
        "head_designation": "Municipal Commissioner",
        "contact_email": "nnlko@nic.in",
        "helpline_number": "1533",
        "emergency_number": "1800-180-0522",
        "office_address": "Trilokinath Marg, Lalbagh, Lucknow - 226001, Uttar Pradesh",
        "description": (
            "Handles roads, potholes, garbage collection, street lighting, "
            "stray animals, and encroachment within Lucknow city limits."
        ),
        "sla_hours": 72,
    },
    {
        "name": "Jal Sansthan / Jalkal Vibhag, Lucknow (Water & Drainage)",
        "slug": "jal-sansthan-lucknow",
        "head_designation": "Executive Engineer, Jalkal Vibhag",
        "contact_email": "nnlko@nic.in",
        "helpline_number": "8177054003",
        "emergency_number": "8177054003",
        "office_address": "Water Works Road, Aishbagh, Lucknow, Uttar Pradesh",
        "description": (
            "Handles piped water supply, water quality, sewage overflow, and "
            "drainage/waterlogging complaints in Lucknow."
        ),
        "sla_hours": 48,
    },
    {
        "name": "MVVNL — Madhyanchal Vidyut Vitran Nigam (Power / Discom)",
        "slug": "mvvnl-lucknow",
        "head_designation": "Managing Director, MVVNL",
        "contact_email": "cccmvvnl1912@gmail.com",
        "helpline_number": "1912",
        "emergency_number": "18001800440",
        "office_address": "4-A, Gokhale Marg, Lucknow, Uttar Pradesh - 226001",
        "description": (
            "Handles power outages, sparking, transformer faults, voltage "
            "issues, and electricity billing complaints across Lucknow."
        ),
        "sla_hours": 24,
    },
    {
        "name": "Traffic & Urban Mobility (UP Traffic Directorate)",
        "slug": "traffic-directorate-up",
        "head_designation": "Director, Traffic, UP Police",
        "contact_email": "dirtraffic-up@nic.in",
        "helpline_number": "1073",
        "emergency_number": "112",
        "office_address": "UP Police Headquarters, Lucknow, Uttar Pradesh",
        "description": (
            "Handles traffic signal faults, illegal parking, encroached "
            "roads, and traffic-flow complaints."
        ),
        "sla_hours": 48,
    },
    {
        "name": "Public Health Department (CMO Lucknow)",
        "slug": "public-health-lucknow",
        "head_designation": "Chief Medical Officer (CMO), Lucknow",
        "contact_email": "cmolko@gmail.com",
        "helpline_number": "05222622080",
        "emergency_number": "108",
        "office_address": "Office of the CMO, Lucknow, Uttar Pradesh",
        "description": (
            "Handles mosquito/vector-borne disease control, hospital "
            "sanitation, and public-health emergencies."
        ),
        "sla_hours": 24,
    },
]

SECTORS = [
    ("roads-potholes", "Potholes & Road Damage", "construction", "nagar-nigam-lucknow"),
    ("garbage-collection", "Garbage Collection", "trash-2", "nagar-nigam-lucknow"),
    ("street-lighting", "Street Lighting", "lightbulb", "nagar-nigam-lucknow"),
    ("stray-animals", "Stray Animals", "dog", "nagar-nigam-lucknow"),
    ("illegal-encroachment", "Illegal Encroachment", "alert-octagon", "nagar-nigam-lucknow"),
    ("water-supply", "Water Supply", "droplet", "jal-sansthan-lucknow"),
    ("sewage-drainage", "Sewage & Drainage", "waves", "jal-sansthan-lucknow"),
    ("power-outage", "Power Outage & Faults", "zap", "mvvnl-lucknow"),
    ("power-billing", "Electricity Billing", "receipt", "mvvnl-lucknow"),
    ("traffic-signal", "Traffic Signal Fault", "traffic-cone", "traffic-directorate-up"),
    ("illegal-parking", "Illegal Parking / Traffic", "car", "traffic-directorate-up"),
    ("mosquito-disease-control", "Mosquito & Disease Control", "bug", "public-health-lucknow"),
    ("hospital-sanitation", "Hospital Sanitation", "hospital", "public-health-lucknow"),
]


class Command(BaseCommand):
    help = "Seeds/re-confirms the 5 Lucknow departments and 13 grievance categories."

    def handle(self, *args, **options):
        dept_objs = {}
        for d in DEPARTMENTS:
            obj, created = Department.objects.update_or_create(
                slug=d["slug"], defaults=d
            )
            dept_objs[d["slug"]] = obj
            status = "created" if created else "already existed (data refreshed)"
            self.stdout.write(f"  Department '{obj.name}' — {status}, email: {obj.contact_email}")

        for slug, name, icon, dept_slug in SECTORS:
            sector, created = Sector.objects.get_or_create(
                slug=slug, defaults={"name": name, "icon": icon}
            )
            sector.departments.add(dept_objs[dept_slug])
            status = "created" if created else "already existed"
            self.stdout.write(f"  Sector '{sector.name}' — {status}, linked to {dept_objs[dept_slug].name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {Department.objects.count()} departments, {Sector.objects.count()} sectors in DB."
        ))
