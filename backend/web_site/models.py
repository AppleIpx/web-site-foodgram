from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=30,
        unique=True
    )
    BLUE = "#0000FF"
    RED = "#FF0000"
    GREEN = "#008000"
    YELLOW = "#FFFF00"
    COLOR_CHOICE = [
        (BLUE, "Синий"),
        (RED, "Красный"),
        (GREEN, "Зеленый"),
        (YELLOW, "Желтый")
    ]
    color = models.CharField(
        verbose_name="Цвет",
        choices=COLOR_CHOICE,
        unique=True,
        max_length=30
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=250
    )
    image = models.ImageField()
    text = models.TextField(verbose_name="Текстовое описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиенты",
        through='IngredientInRecipe',
        related_name="recipes"
    )
    # through это связка с IngredientInRecipe как будет называться таблица в бд
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэг",
        through="TagsInRecipe",
        related_name="recipes"
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Время публикации",
        editable=False
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.IntegerField(
        verbose_name="количество",
        validators=[MinValueValidator(1)],
        null=True
    )

    class Meta:
        verbose_name = "Ингредиенты в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient'
                ],
                name='unique_combination'
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class TagsInRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name="Тэг в рецепте",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = verbose_name = "Тэги в рецепте"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="favorite",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="favorite",
        on_delete=models.CASCADE
    )  # related_name используется для обратной связи
    # от recipe к Favorite. Таким образом можно получить доступ к списку избранным резептам пользователя.
    when_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["when_added"]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = verbose_name
        unique_together = (
            "user",
            "recipe"
        )

    def __str__(self):
        return f"{self.user} added {self.recipe}"


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт в списке покупок",
        related_name="shopping_cart",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="shopping_cart",
        on_delete=models.CASCADE
    )
    when_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["when_added"]
        verbose_name = "Список покупки"
        verbose_name_plural = "Список покупок"

        # Делаем эти значения в бд уникальными
        unique_together = (
            "user",
            "recipe"
        )

    def __str__(self):
        return f"{self.user} added {self.recipe}"
