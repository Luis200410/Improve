import random
from typing import Sequence

from django.core.management.base import BaseCommand
from django.db import transaction

from personal_management import models


EXERCISE_CATEGORIES = [
    ("Strength", "Compound and isolation lifts for building strength and hypertrophy."),
    ("Mobility", "Dynamic and static movements to improve joint range of motion."),
    ("Conditioning", "Cardio, intervals, and metabolic conditioning work."),
    ("Core", "Midline stability and rotational strength exercises."),
    ("Recovery", "Light movements for tissue recovery and activation."),
]

MUSCLE_NAMES = [choice[0] for choice in models.Exercise.MUSCLE_GROUP_CHOICES]

COACHING_CUES = [
    "- Maintain a neutral spine throughout the movement.",
    "- Keep your core braced and ribs stacked over pelvis.",
    "- Move with control on the eccentric; explode on the concentric.",
    "- Drive through the full foot and avoid collapsing arches.",
    "- Align knees with the second toe; avoid valgus collapse.",
    "- Keep shoulders packed and avoid shrugging.",
    "- Exhale through the effort, inhale on the reset.",
]

EQUIPMENT_CHOICES: Sequence[str] = [
    models.Exercise.BODYWEIGHT,
    models.Exercise.DUMBBELL,
    models.Exercise.BARBELL,
    models.Exercise.MACHINE,
    models.Exercise.KETTLEBELL,
    models.Exercise.BAND,
]


class Command(BaseCommand):
    help = "Populate the Body libraries with synthetic data (exercises and meals)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=3000,
            help="Number of exercises to seed (default: 3000).",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="If provided, existing generated exercises will be deleted before seeding.",
        )
        parser.add_argument(
            "--meal-count",
            type=int,
            default=10000,
            help="Number of meals to seed (default: 10000).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count: int = options["count"]
        overwrite: bool = options["overwrite"]
        meal_count: int = options["meal_count"]

        if overwrite:
            self.stdout.write("Removing previously generated exercises…")
            models.Exercise.objects.filter(
                name__startswith="Auto Exercise "
            ).delete()
            self.stdout.write("Removing previously generated meals…")
            models.Meal.objects.filter(
                name__startswith="Auto Meal "
            ).delete()

        categories = self._ensure_categories()
        meal_categories = self._ensure_meal_categories()
        created = 0

        self.stdout.write(f"Seeding {count} exercises into the library…")
        for index in range(1, count + 1):
            name = f"Auto Exercise {index:04d}"
            if models.Exercise.objects.filter(name=name).exists():
                continue

            category = random.choice(categories)
            equipment = random.choice(EQUIPMENT_CHOICES)
            primary = random.sample(MUSCLE_NAMES, k=2)
            secondary = random.sample(
                [name for name in MUSCLE_NAMES if name not in primary], k=2
            )
            cues = "\n".join(random.sample(COACHING_CUES, k=3))

            models.Exercise.objects.create(
                name=name,
                category=category,
                equipment=equipment,
                primary_muscles=primary,
                secondary_muscles=secondary,
                description=(
                    f"{name} is a programmed movement designed to build capacity in the "
                    f"{primary.lower()} while reinforcing sound mechanics."
                ),
                coaching_cues=cues,
                image_url=f"https://picsum.photos/seed/exercise-{index}/640/480",
                video_url=f"https://videos.example.com/exercise-{index}.mp4",
            )
            created += 1

            if created % 250 == 0:
                self.stdout.write(f"  Created {created} exercises…")

        self.stdout.write(self.style.SUCCESS(f"Exercise seeding complete. Added {created} exercises."))

        self.stdout.write(f"Seeding {meal_count} meals across dietary libraries…")
        created_meals = 0
        for index in range(1, meal_count + 1):
            name = f"Auto Meal {index:05d}"
            if models.Meal.objects.filter(name=name).exists():
                continue

            category = random.choice(meal_categories)
            calories = random.randint(300, 900)
            protein = round(random.uniform(15, 60), 1)
            carbs = round(random.uniform(20, 120), 1)
            fats = round(random.uniform(5, 45), 1)
            servings = random.randint(1, 4)

            ingredients = "\n".join(
                f"- Ingredient {i}" for i in range(1, random.randint(4, 9))
            )
            instructions = "\n".join(
                [
                    "1. Prepare ingredients and preheat appliances as needed.",
                    "2. Cook following the recommended method for this diet style.",
                    "3. Plate, taste, and adjust seasoning to preference.",
                ]
            )

            models.Meal.objects.create(
                name=name,
                category=category,
                summary=f"{category.name} friendly meal to support training and recovery.",
                ingredients=ingredients,
                instructions=instructions,
                servings=servings,
                calories=calories,
                protein=protein,
                carbohydrates=carbs,
                fats=fats,
                prep_time_minutes=random.randint(10, 45),
                image_url=f"https://picsum.photos/seed/meal-{index}/640/480",
                recipe_url=f"https://recipes.example.com/meal-{index}",
            )
            created_meals += 1

            if created_meals % 500 == 0:
                self.stdout.write(f"  Created {created_meals} meals…")

        self.stdout.write(self.style.SUCCESS(f"Meal seeding complete. Added {created_meals} meals."))

    def _ensure_categories(self) -> list[models.ExerciseCategory]:
        categories: list[models.ExerciseCategory] = []
        for name, description in EXERCISE_CATEGORIES:
            category, _ = models.ExerciseCategory.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            categories.append(category)
        return categories

    def _ensure_meal_categories(self) -> list[models.MealCategory]:
        diets = [
            "Carnivore",
            "Ketogenic",
            "Paleo",
            "Mediterranean",
            "Vegetarian",
            "Vegan",
            "Pescatarian",
            "Flexitarian",
            "Whole30",
            "Gluten-Free",
            "Low-FODMAP",
            "Diabetic-Friendly",
            "DASH",
            "Ayurvedic",
            "Macrobiotic",
            "Raw Food",
            "Nordic",
            "MIND Diet",
            "Anti-Inflammatory",
            "High-Protein",
            "Low-Carb",
            "Low-Fat",
            "Plant-Based Athletic",
            "Pregnancy Support",
            "Post-Workout Recovery",
        ]
        categories: list[models.MealCategory] = []
        for diet in diets:
            category, _ = models.MealCategory.objects.get_or_create(
                name=diet,
                defaults={
                    "description": f"Recipes tailored for the {diet} approach."
                },
            )
            categories.append(category)
        return categories
