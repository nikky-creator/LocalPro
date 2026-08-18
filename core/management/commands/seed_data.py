import random
from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile
from bookings.models import Booking
from core.models import Testimonial
from payments.models import Payment
from reports.models import Report
from reviews.models import Review
from services.models import CITY_COORDS, Provider, ServiceCategory

CATEGORIES = [
    ('Electrician', 'fa-solid fa-bolt', 'green', 'Wiring, fittings, repairs and installations.'),
    ('Plumber', 'fa-solid fa-faucet-drip', 'navy', 'Leak repairs, fittings, and pipeline work.'),
    ('Painter', 'fa-solid fa-paint-roller', 'blue', 'Interior and exterior painting, texture work.'),
    ('Cleaner', 'fa-solid fa-broom', 'green', 'Home deep cleaning and regular upkeep.'),
    ('Mechanic', 'fa-solid fa-screwdriver-wrench', 'gold', 'Two and four-wheeler repair and servicing.'),
    ('Tutor', 'fa-solid fa-graduation-cap', 'orange', 'School, college and competitive exam tutoring.'),
    ('Carpenter', 'fa-solid fa-hammer', 'navy', 'Furniture, fittings, and woodwork repairs.'),
    ('AC Technician', 'fa-solid fa-fan', 'blue', 'AC installation, servicing, and gas refill.'),
]

CITIES = ['Vijayawada', 'Guntur', 'Vishakhapatnam', 'Rajahmundry', 'Eluru']
AREAS = ['Governorpet', 'MG Road', 'Benz Circle', 'Patamata', 'Gunadala', 'Suryaraopet', 'Autonagar', 'Ring Road']

FIRST_NAMES_M = ['Ramesh', 'Suresh', 'Venkat', 'Krishna', 'Arjun', 'Praveen', 'Naveen', 'Siva', 'Ravi', 'Mahesh', 'Kiran', 'Sandeep']
FIRST_NAMES_F = ['Lakshmi', 'Priya', 'Divya', 'Swathi', 'Sravani', 'Anitha', 'Kavya', 'Bhavani', 'Sowmya', 'Padma']
LAST_NAMES = ['Kumar', 'Reddy', 'Rao', 'Varma', 'Naidu', 'Chowdary', 'Prasad', 'Babu', 'Sharma', 'Naik']

PROVIDER_BIOS = [
    "Reliable and punctual, with a focus on clean, lasting work. Fully equipped for same-day jobs.",
    "Years of hands-on experience across residential and small commercial projects in the area.",
    "Friendly service with transparent pricing — no hidden charges, ever. Happy to give free estimates.",
    "Specializes in quick turnarounds without compromising quality. Available for emergency call-outs.",
    "Detail-oriented professional who takes pride in every job, big or small.",
]

CUSTOMER_REVIEWS = [
    "Excellent work, arrived on time and finished quickly. Highly recommend!",
    "Very professional and polite. Explained everything clearly before starting.",
    "Good service overall, fair pricing. Would book again.",
    "Fixed the issue in no time. Very knowledgeable.",
    "Solid work, though arrived a little later than expected.",
    "Outstanding attention to detail. My place has never looked better.",
    "Quick, clean, and courteous. Exactly what I needed.",
    "Reasonable rate and honest advice on what actually needed fixing.",
]

REPORT_DESCRIPTIONS = {
    'no_show': "Waited over an hour past the scheduled time and the provider never arrived or called to reschedule.",
    'poor_quality': "The work was rushed and had to be redone by someone else a week later.",
    'overcharged': "Was quoted one price beforehand but charged significantly more after the job was done.",
    'unprofessional': "Provider was rude on the phone and left the work area messy.",
}

TESTIMONIALS = [
    ("Anjali Rao", "Homeowner, Vijayawada", "Booking an electrician used to be such a hassle. With LocalPro I found a verified pro in minutes and the job was done the same evening.", 5),
    ("Karthik Reddy", "Working Professional, Guntur", "The transparent pricing and real reviews gave me a lot of confidence before booking. Great experience end to end.", 5),
    ("Deepika Naidu", "Homeowner, Vishakhapatnam", "I've used LocalPro three times now for cleaning and painting. Consistently good providers every time.", 4),
    ("Ravi Teja", "Provider, Electrician", "As a provider, the dashboard makes it so easy to manage bookings and track my ratings. My bookings have doubled.", 5),
    ("Sneha Patnaik", "Homeowner, Eluru", "Loved how easy it was to compare providers by price and rating before booking. Saved me a lot of time.", 4),
    ("Manoj Kumar", "Provider, Plumber", "Great platform to reach new customers in my area. Support has also been quick to respond whenever I had questions.", 5),
]


class Command(BaseCommand):
    help = 'Seeds the database with demo categories, providers, customers, bookings, and reviews.'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing demo data before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        if options['flush']:
            self.stdout.write('Flushing existing demo data...')
            Report.objects.all().delete()
            Payment.objects.all().delete()
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Provider.objects.all().delete()
            ServiceCategory.objects.all().delete()
            Testimonial.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        categories = self._seed_categories()
        providers = self._seed_providers(categories)
        customers = self._seed_customers()
        self._seed_bookings_and_reviews(providers, customers)
        self._seed_testimonials()

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Seeded {len(categories)} categories, {len(providers)} providers, '
            f'{len(customers)} customers, plus bookings, payments, reviews, reports, and testimonials.'
        ))
        self.stdout.write(self.style.WARNING('\nSample login credentials (password for all: DemoPass123):'))
        self.stdout.write('  Customers: customer1 .. customer8')
        self.stdout.write('  Providers: provider1 .. provider16')

    def _seed_categories(self):
        self.stdout.write('Seeding categories...')
        categories = []
        for i, (name, icon, color, desc) in enumerate(CATEGORIES):
            cat, _ = ServiceCategory.objects.get_or_create(
                name=name, defaults={'icon': icon, 'color': color, 'description': desc, 'order': i}
            )
            categories.append(cat)
        return categories

    def _make_user(self, username, first, last, email, role):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': email}
        )
        if created:
            user.set_password('DemoPass123')
            user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.phone = f'9{random.randint(100000000, 999999999)}'
        profile.city = random.choice(CITIES)
        if role == Profile.ROLE_CUSTOMER:
            profile.address = f'{random.randint(1, 99)}-{random.randint(1,20)}-{random.randint(1,50)}, {random.choice(AREAS)}'
        profile.save()
        return user

    def _seed_providers(self, categories):
        self.stdout.write('Seeding providers...')
        providers = []
        idx = 1
        for cat in categories:
            for _ in range(2):
                is_male = random.random() > 0.35
                first = random.choice(FIRST_NAMES_M if is_male else FIRST_NAMES_F)
                last = random.choice(LAST_NAMES)
                username = f'provider{idx}'
                user = self._make_user(username, first, last, f'{username}@localpro.example', Profile.ROLE_PROVIDER)

                city = random.choice(CITIES)
                base_lat, base_lng = CITY_COORDS.get(city.lower(), (16.5062, 80.6480))
                provider, _ = Provider.objects.get_or_create(
                    user=user,
                    defaults={
                        'category': cat,
                        'business_name': f'{first} {cat.name} Services' if random.random() > 0.5 else '',
                        'bio': random.choice(PROVIDER_BIOS),
                        'experience_years': random.randint(1, 18),
                        'price_per_hour': random.choice([250, 300, 350, 400, 450, 500, 600, 700, 800]),
                        'location': random.choice(AREAS),
                        'city': city,
                        'latitude': round(base_lat + random.uniform(-0.025, 0.025), 6),
                        'longitude': round(base_lng + random.uniform(-0.025, 0.025), 6),
                        'is_available': random.random() > 0.12,
                        'availability_days': ','.join(random.sample(
                            ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], k=random.randint(4, 7)
                        )),
                        'availability_start': time(9, 0),
                        'availability_end': time(random.choice([17, 18, 19, 20]), 0),
                        'is_verified': random.random() > 0.15,
                    }
                )
                providers.append(provider)
                idx += 1
        return providers

    def _seed_customers(self):
        self.stdout.write('Seeding customers...')
        customers = []
        for i in range(1, 9):
            is_male = random.random() > 0.5
            first = random.choice(FIRST_NAMES_M if is_male else FIRST_NAMES_F)
            last = random.choice(LAST_NAMES)
            username = f'customer{i}'
            user = self._make_user(username, first, last, f'{username}@localpro.example', Profile.ROLE_CUSTOMER)
            customers.append(user)
        return customers

    def _seed_bookings_and_reviews(self, providers, customers):
        self.stdout.write('Seeding bookings and reviews...')
        statuses_pool = (
            [Booking.STATUS_COMPLETED] * 5
            + [Booking.STATUS_ACCEPTED] * 2
            + [Booking.STATUS_PENDING] * 2
            + [Booking.STATUS_REJECTED] * 1
            + [Booking.STATUS_CANCELLED] * 1
        )
        today = date.today()

        for provider in providers:
            num_bookings = random.randint(2, 6)
            chosen_customers = random.sample(customers, k=min(num_bookings, len(customers)))
            for customer in chosen_customers:
                status = random.choice(statuses_pool)
                if status == Booking.STATUS_PENDING:
                    service_date = today + timedelta(days=random.randint(1, 14))
                elif status == Booking.STATUS_ACCEPTED:
                    service_date = today + timedelta(days=random.randint(0, 10))
                else:
                    service_date = today - timedelta(days=random.randint(1, 90))

                booking = Booking.objects.create(
                    customer=customer,
                    provider=provider,
                    service_date=service_date,
                    service_time=time(random.choice([9, 10, 11, 13, 14, 15, 16, 17]), random.choice([0, 30])),
                    address=f'{random.randint(1,99)}-{random.randint(1,20)}, {random.choice(AREAS)}, {provider.city}',
                    notes=random.choice(['', '', 'Please call before arriving.', 'Gate code is at the entrance.']),
                    status=status,
                )

                if status == Booking.STATUS_COMPLETED and random.random() > 0.25:
                    Review.objects.create(
                        booking=booking,
                        customer=customer,
                        provider=provider,
                        rating=random.choice([3, 4, 4, 5, 5, 5]),
                        comment=random.choice(CUSTOMER_REVIEWS),
                    )

                if status == Booking.STATUS_COMPLETED and random.random() > 0.35:
                    from django.utils import timezone as tz
                    Payment.objects.create(
                        booking=booking,
                        customer=customer,
                        amount=provider.price_per_hour,
                        method=random.choice(['card', 'upi', 'netbanking']),
                        status=Payment.STATUS_SUCCESS,
                        paid_at=tz.now(),
                    )

                if status in (Booking.STATUS_COMPLETED, Booking.STATUS_REJECTED) and random.random() > 0.9:
                    reason = random.choice(list(REPORT_DESCRIPTIONS.keys()))
                    Report.objects.create(
                        booking=booking,
                        customer=customer,
                        provider=provider,
                        reason=reason,
                        description=REPORT_DESCRIPTIONS[reason],
                        status=random.choice(['open', 'under_review', 'resolved']),
                    )

    def _seed_testimonials(self):
        self.stdout.write('Seeding testimonials...')
        for i, (name, role, quote, rating) in enumerate(TESTIMONIALS):
            Testimonial.objects.get_or_create(
                author_name=name, defaults={'author_role': role, 'quote': quote, 'rating': rating, 'order': i}
            )
