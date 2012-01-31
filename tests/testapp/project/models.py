# -*- coding: utf-8 -*-
from django.db import models
from shop.models.productmodel import Product


class DiaryProduct(Product):
    isbn = models.CharField(max_length=255)
    number_of_pages = models.IntegerField()
