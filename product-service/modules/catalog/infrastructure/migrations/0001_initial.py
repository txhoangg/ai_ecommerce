from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookTypeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_key', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('name_vi', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('attribute_schema', models.JSONField(default=dict)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'book_types',
                'ordering': ['name'],
                'app_label': 'catalog',
            },
        ),
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='children',
                    to='catalog.categorymodel'
                )),
            ],
            options={
                'db_table': 'categories',
                'ordering': ['name'],
                'app_label': 'catalog',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='PublisherModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'publishers',
                'ordering': ['name'],
                'app_label': 'catalog',
            },
        ),
        migrations.CreateModel(
            name='BookModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('isbn', models.CharField(blank=True, max_length=20)),
                ('image_url', models.URLField(blank=True, max_length=1000)),
                ('attributes', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='books',
                    to='catalog.booktypemodel'
                )),
                ('category', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='books',
                    to='catalog.categorymodel'
                )),
                ('publisher', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='books',
                    to='catalog.publishermodel'
                )),
            ],
            options={
                'db_table': 'books',
                'ordering': ['-created_at'],
                'app_label': 'catalog',
            },
        ),
        migrations.AddIndex(
            model_name='bookmodel',
            index=models.Index(fields=['book_type'], name='books_book_type_idx'),
        ),
        migrations.AddIndex(
            model_name='bookmodel',
            index=models.Index(fields=['category'], name='books_category_idx'),
        ),
        migrations.AddIndex(
            model_name='bookmodel',
            index=models.Index(fields=['is_active'], name='books_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='bookmodel',
            index=models.Index(fields=['price'], name='books_price_idx'),
        ),
    ]
