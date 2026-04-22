"""
Seed script — populate the database with sample categories and cards.
Run: python seed_data.py
"""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'slab_lab.settings'
django.setup()

from django.contrib.auth.models import User
from apps.catalogue.models import Category, Card

admin = User.objects.get(username='admin')

# ── Categories ───────────────────────────────────────────────────────────────
categories_data = [
    {'name': 'Pokémon', 'slug': 'pokemon', 'description': 'Pokémon Trading Card Game collectibles', 'children': [
        {'name': 'Base Set', 'slug': 'pokemon-base-set', 'description': 'Original 1999 Base Set'},
        {'name': 'Modern', 'slug': 'pokemon-modern', 'description': 'Recent Pokémon TCG expansions'},
        {'name': 'Japanese', 'slug': 'pokemon-japanese', 'description': 'Japanese print Pokémon cards'},
    ]},
    {'name': 'Sports', 'slug': 'sports', 'description': 'Graded sports trading cards', 'children': [
        {'name': 'Basketball', 'slug': 'sports-basketball', 'description': 'NBA player cards'},
        {'name': 'Baseball', 'slug': 'sports-baseball', 'description': 'MLB player cards'},
        {'name': 'Football', 'slug': 'sports-football', 'description': 'NFL player cards'},
    ]},
    {'name': 'Yu-Gi-Oh!', 'slug': 'yugioh', 'description': 'Yu-Gi-Oh! collectible cards', 'children': [
        {'name': 'Legend of Blue Eyes', 'slug': 'yugioh-lob', 'description': 'First English set'},
    ]},
    {'name': 'Magic: The Gathering', 'slug': 'mtg', 'description': 'MTG collectible cards', 'children': [
        {'name': 'Alpha/Beta', 'slug': 'mtg-alpha-beta', 'description': 'Original Alpha and Beta prints'},
    ]},
]

print("Creating categories...")
for cat_data in categories_data:
    children = cat_data.pop('children', [])
    parent, _ = Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
    print(f"  ✓ {parent.name}")
    for child_data in children:
        child, _ = Category.objects.get_or_create(slug=child_data['slug'], defaults={**child_data, 'parent': parent})
        print(f"    ↳ {child.name}")

# ── Cards ────────────────────────────────────────────────────────────────────
cards_data = [
    # Pokémon Base Set
    {'title': 'Charizard 1st Edition Holo #4', 'category_slug': 'pokemon-base-set', 'set_name': 'Base Set', 'edition': '1st Edition', 'rarity': 'ultra_rare', 'condition': 'near_mint', 'brand': 'Pokémon', 'grading_company': 'psa', 'grade': 9.0, 'year': 1999, 'price': 42500.00, 'stock': 1, 'featured': True, 'description': 'The holy grail of Pokémon cards. 1st Edition Base Set Charizard in PSA 9 condition. Iconic artwork by Mitsuhiro Arita.', 'population': 2691, 'serial_number': 'PSA-48291837'},
    {'title': 'Blastoise Holo #2 Base Set', 'category_slug': 'pokemon-base-set', 'set_name': 'Base Set', 'edition': 'Unlimited', 'rarity': 'rare', 'condition': 'excellent', 'brand': 'Pokémon', 'grading_company': 'bgs', 'grade': 8.5, 'year': 1999, 'price': 850.00, 'stock': 2, 'description': 'Classic Blastoise holographic from the original Base Set. BGS 8.5 with strong subgrades.'},
    {'title': 'Pikachu Red Cheeks #58 E3 Promo', 'category_slug': 'pokemon-base-set', 'set_name': 'E3 Promo', 'edition': 'Promo', 'rarity': 'promo', 'condition': 'mint', 'brand': 'Pokémon', 'grading_company': 'psa', 'grade': 10.0, 'year': 1998, 'price': 5200.00, 'stock': 1, 'featured': True, 'description': 'Extremely rare E3 Promo Pikachu with red cheeks error. Gem Mint PSA 10.', 'population': 89},
    {'title': 'Mewtwo Holo #10 Base Set', 'category_slug': 'pokemon-base-set', 'set_name': 'Base Set', 'edition': 'Unlimited', 'rarity': 'rare', 'condition': 'near_mint', 'brand': 'Pokémon', 'grading_company': 'cgc', 'grade': 8.0, 'year': 1999, 'price': 320.00, 'stock': 3, 'description': 'Fan favorite Mewtwo holographic. CGC 8.0 in excellent condition.'},
    # Pokémon Modern
    {'title': 'Umbreon VMAX Alt Art #215', 'category_slug': 'pokemon-modern', 'set_name': 'Evolving Skies', 'edition': 'Regular', 'rarity': 'secret_rare', 'condition': 'mint', 'brand': 'Pokémon', 'grading_company': 'psa', 'grade': 10.0, 'year': 2021, 'price': 1100.00, 'stock': 1, 'featured': True, 'description': 'The most sought-after modern Pokémon card. Stunning alternate art illustration.', 'population': 4215},
    {'title': 'Moonbreon VMAX TG #30', 'category_slug': 'pokemon-modern', 'set_name': 'Brilliant Stars', 'edition': 'Trainer Gallery', 'rarity': 'ultra_rare', 'condition': 'near_mint', 'brand': 'Pokémon', 'grading_company': 'psa', 'grade': 9.0, 'year': 2022, 'price': 280.00, 'stock': 2, 'description': 'Beautiful Trainer Gallery variant of Umbreon VMAX.'},
    # Sports — Basketball
    {'title': 'LeBron James Topps Chrome RC #111', 'category_slug': 'sports-basketball', 'set_name': 'Topps Chrome', 'edition': 'Rookie', 'rarity': 'rare', 'condition': 'near_mint', 'brand': 'Topps', 'grading_company': 'psa', 'grade': 9.0, 'year': 2003, 'price': 28000.00, 'stock': 1, 'featured': True, 'description': 'LeBron James rookie card from 2003 Topps Chrome. Iconic investment piece.', 'population': 1847},
    {'title': 'Michael Jordan Fleer RC #57', 'category_slug': 'sports-basketball', 'set_name': 'Fleer', 'edition': 'Rookie', 'rarity': 'ultra_rare', 'condition': 'excellent', 'brand': 'Fleer', 'grading_company': 'bgs', 'grade': 8.0, 'year': 1986, 'price': 52000.00, 'stock': 1, 'description': 'The GOAT rookie card. 1986 Fleer Michael Jordan in BGS 8.', 'population': 3691},
    # Sports — Baseball
    {'title': 'Mike Trout Topps Update RC #US175', 'category_slug': 'sports-baseball', 'set_name': 'Topps Update', 'edition': 'Rookie', 'rarity': 'rare', 'condition': 'mint', 'brand': 'Topps', 'grading_company': 'psa', 'grade': 10.0, 'year': 2011, 'price': 4800.00, 'stock': 1, 'description': 'Mike Trout gem mint rookie card. One of the best modern baseball investments.'},
    # Yu-Gi-Oh!
    {'title': 'Blue-Eyes White Dragon LOB-001', 'category_slug': 'yugioh-lob', 'set_name': 'Legend of Blue Eyes White Dragon', 'edition': '1st Edition', 'rarity': 'ultra_rare', 'condition': 'near_mint', 'brand': 'Yu-Gi-Oh!', 'grading_company': 'psa', 'grade': 9.0, 'year': 2002, 'price': 12500.00, 'stock': 1, 'featured': True, 'description': 'Iconic 1st Edition Blue-Eyes White Dragon. The most recognizable Yu-Gi-Oh! card ever printed.', 'population': 841},
    {'title': 'Dark Magician SDY-006 1st Edition', 'category_slug': 'yugioh-lob', 'set_name': 'Starter Deck Yugi', 'edition': '1st Edition', 'rarity': 'rare', 'condition': 'near_mint', 'brand': 'Yu-Gi-Oh!', 'grading_company': 'cgc', 'grade': 8.5, 'year': 2002, 'price': 980.00, 'stock': 2, 'description': 'Yugi\'s signature monster in 1st Edition from the original Starter Deck.'},
    # MTG
    {'title': 'Black Lotus Alpha', 'category_slug': 'mtg-alpha-beta', 'set_name': 'Alpha', 'edition': 'Alpha', 'rarity': 'ultra_rare', 'condition': 'good', 'brand': 'Magic: The Gathering', 'grading_company': 'bgs', 'grade': 7.0, 'year': 1993, 'price': 185000.00, 'stock': 1, 'featured': True, 'description': 'The most valuable trading card in history. Alpha Black Lotus graded BGS 7.', 'population': 48},
    # Common/Budget options
    {'title': 'Pikachu #25 Jungle Set', 'category_slug': 'pokemon-base-set', 'set_name': 'Jungle', 'edition': 'Unlimited', 'rarity': 'common', 'condition': 'near_mint', 'brand': 'Pokémon', 'grading_company': 'raw', 'grade': None, 'year': 1999, 'price': 18.00, 'stock': 15, 'description': 'Cute Pikachu from the classic Jungle expansion. Great starter collectible.'},
    {'title': 'Steph Curry Prizm Base #49', 'category_slug': 'sports-basketball', 'set_name': 'Prizm', 'edition': 'Base', 'rarity': 'uncommon', 'condition': 'near_mint', 'brand': 'Panini', 'grading_company': 'raw', 'grade': None, 'year': 2020, 'price': 35.00, 'stock': 8, 'description': 'Stephen Curry base Prizm card in great raw condition.'},
    {'title': 'Gengar Holo VMAX #271', 'category_slug': 'pokemon-modern', 'set_name': 'Fusion Strike', 'edition': 'Regular', 'rarity': 'ultra_rare', 'condition': 'mint', 'brand': 'Pokémon', 'grading_company': 'psa', 'grade': 10.0, 'year': 2021, 'price': 95.00, 'stock': 5, 'description': 'Spooky Gengar VMAX in gem mint PSA 10. Popular collector card.'},
    {'title': 'Shohei Ohtani Bowman Chrome 1st #1', 'category_slug': 'sports-baseball', 'set_name': 'Bowman Chrome', 'edition': '1st Bowman', 'rarity': 'rare', 'condition': 'near_mint', 'brand': 'Topps', 'grading_company': 'psa', 'grade': 9.5, 'year': 2018, 'price': 3200.00, 'stock': 1, 'description': '2018 Bowman Chrome 1st of the two-way superstar. Key modern baseball card.'},
]

print("\nCreating cards...")
for card_data in cards_data:
    cat_slug = card_data.pop('category_slug')
    category = Category.objects.get(slug=cat_slug)
    card_data['category'] = category
    card_data['seller'] = admin

    if not Card.objects.filter(title=card_data['title']).exists():
        card = Card(**card_data)
        card.save()
        print(f"  ✓ {card.title} — ${card.price}")
    else:
        print(f"  ○ {card_data['title']} (exists)")

print(f"\nDone! {Card.objects.count()} cards, {Category.objects.count()} categories in database.")
