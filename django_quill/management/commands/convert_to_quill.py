import json
from json.decoder import JSONDecodeError

from django.apps import apps
from django.core.management import BaseCommand

from django_quill.fields import FieldQuill


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("app_label", type=str)
        parser.add_argument("model_name", type=str)
        parser.add_argument("field_name", type=str)

    def handle(self, *args, **options):
        app_label = options["app_label"]
        model_name = options["model_name"]
        field_name = options["field_name"]

        model = apps.get_registered_model(app_label, model_name)
        instances = model.objects.all()
        for index, instance in enumerate(instances, start=1):
            print(
                f"[{index}/{len(instances)}] {model_name} (pk: {instance.pk}) converting"
            )
            field_data = getattr(instance, field_name)
            if isinstance(field_data, FieldQuill):
                print(f" This is already a QuillField.")
                continue
            try:
                json_data = json.loads(field_data)
                if "delta" in json_data:
                    print(f" Already in Quill format. has been skipped")
                    continue
            except JSONDecodeError:
                print(f" Converted ({field_data[:20]}...)")
            except TypeError:
                print(f" Change type ({type(field_data)} -> str)")
                field_data = str(field_data)
                print(f" Changed value: {field_data[:20]}...")
            finally:
                converted_data = {
                    "delta": "",
                    "html": field_data,
                }
                setattr(instance, field_name, json.dumps(converted_data))
                instance.save()
                print(f" Saved")
