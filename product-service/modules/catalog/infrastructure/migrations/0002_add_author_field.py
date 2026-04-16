from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "ALTER TABLE books ADD COLUMN IF NOT EXISTS author varchar(300);",
                        "UPDATE books SET author = '' WHERE author IS NULL;",
                        "ALTER TABLE books ALTER COLUMN author SET DEFAULT '';",
                        "ALTER TABLE books ALTER COLUMN author SET NOT NULL;",
                        "ALTER TABLE books ALTER COLUMN author DROP DEFAULT;",
                    ],
                    reverse_sql="ALTER TABLE books DROP COLUMN IF EXISTS author;",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='bookmodel',
                    name='author',
                    field=models.CharField(blank=True, max_length=300),
                ),
            ],
        ),
    ]
