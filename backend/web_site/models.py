from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тега', max_length=30, unique=True)
    BLUE = "#0000FF"
    RED = "#FF0000"
    GREEN = "#008000"
    YELLOW = "#FFFF00"
    COLOR_CHOICE = [(BLUE, "Синий"), (RED, "Красный"), (GREEN, "Зеленый"), (YELLOW, "Желтый")]
    color = models.CharField(verbose_name="Цвет", choices=COLOR_CHOICE, unique=True, max_length=30)
    slug = models.SlugField(verbose_name="Слаг", unique=True, max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название ингридиента", max_length=200)
    # quantity = models.CharField(verbose_name="Количество", max_length=10)
    measurement_unit = models.CharField(verbose_name="Единица измерения", max_length=200)

    class Meta:
        verbose_name = "Ингредиенты"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name="Автор рецепта", on_delete=models.CASCADE, blank=False, related_name="recipes",)
    title = models.CharField(verbose_name="Название", max_length=250, blank=False, )
    image = models.ImageField(blank=True)
    description = models.TextField(verbose_name="Текстовое описание")
    ingredient = models.ManyToManyField(Ingredient, verbose_name="Ингридиенты", through='IngredientInRecipe', blank=False, related_name="recipes",)
    # through это связка с IngredientInRecipe как будет называться таблица в бд
    tags = models.ManyToManyField(Tag, verbose_name="Тэг", blank=False, through="TagsInRecipe", related_name="recipes",)
    cooking_time = models.PositiveSmallIntegerField(verbose_name="Время приготовления", blank=False, )
    pub_date = models.DateTimeField(auto_now=True, verbose_name="Время публикации", editable=False, )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, verbose_name='ингредиент', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, verbose_name='рецепт', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, verbose_name="количество", decimal_places=2)
    unit = models.CharField(verbose_name="Единица измерения", max_length=20)

    class Meta:
        verbose_name = "Количество ингредиента в рецепте"
        verbose_name_plural = verbose_name


class TagsInRecipe(models.Model):
    tag = models.ForeignKey(Tag, verbose_name="Тэг в рецепте", on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = verbose_name = "Тэги в рецепте"


class Favorite(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", related_name="favorites",
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, verbose_name="Рецепт", related_name="favorites",
                               on_delete=models.CASCADE) #related_name используется для обратной связи
    # от recipe к Favorite. Таким образом можно получить доступ к списку избранным резептам пользователя.
    data_append = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_append"] #Будет происходить сортировка, от новых к старым
        verbose_name = "Избранный рецепт"
        verbose_name_plural = verbose_name
        unique_together = ("user", "recipe")

    def __str__(self):
        return f"{self.user} added {self.recipe}"


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name="Рецепты в списке покупок", related_name="shopping_cart",
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Пользователь", related_name="shopping_cart",
                             on_delete=models.CASCADE)
    data_append = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_append"]
        verbose_name = "Список покупок"
        verbose_name_plural = verbose_name
        unique_together = ("user", "recipe")

    def __str__(self):
        return f"{self.user} added {self.recipe}"

