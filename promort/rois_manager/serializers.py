try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from rois_manager.models import Slice, Core, FocusRegion
from slides_manager.models import Slide


class SliceSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores_count = serializers.SerializerMethodField()
    positive_cores_count = serializers.SerializerMethodField()

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'annotation_step', 'creation_date', 'roi_json',
                  'total_cores', 'positive_cores_count', 'cores_count')
        read_only_fields = ('id', 'creation_date', 'positive_cores_count', 'cores_count')
        write_only_fields = ('annotation_step',)

    def get_cores_count(self, obj):
        return obj.cores.count()

    def get_positive_cores_count(self, obj):
        positive_cores_counter = 0
        cores = CoreSerializer(obj.cores.all(), many=True)
        for core in cores.data:
            if core['positive']:
                positive_cores_counter += 1
        return positive_cores_counter

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class CoreSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    focus_regions_count = serializers.SerializerMethodField()
    positive = serializers.SerializerMethodField()
    normal_tissue_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date', 'roi_json',
                  'length', 'area', 'tumor_length', 'positive', 'focus_regions_count',
                  'normal_tissue_percentage')
        read_only_fields = ('id', 'creation_date', 'positive', 'focus_regions_count',
                            'normal_tissue_percentage')

    def get_focus_regions_count(self, obj):
        return obj.focus_regions.count()

    def get_positive(self, obj):
        for fr in obj.focus_regions.all():
            if fr.cancerous_region:
                return True
        return False

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')

    @staticmethod
    def get_normal_tissue_percentage(obj):
        return obj.get_normal_tissue_percentage()


class FocusRegionSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    core_coverage_percentage = serializers.SerializerMethodField()

    class Meta:
        model = FocusRegion
        fields = ('id', 'label', 'core', 'author', 'creation_date', 'roi_json',
                  'length', 'area', 'cancerous_region', 'core_coverage_percentage')
        read_only_fields = ('id', 'creation_date', 'core_coverage_percentage')

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')

    @staticmethod
    def get_core_coverage_percentage(obj):
        return obj.get_core_coverage_percentage()


class CoreDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    focus_regions = FocusRegionSerializer(many=True, read_only=True)
    positive = serializers.SerializerMethodField()
    normal_tissue_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date', 'roi_json', 'length',
                  'area', 'tumor_length', 'positive', 'focus_regions', 'normal_tissue_percentage')
        read_only_fields = ('id', 'creation_date', 'positive', 'normal_tissue_percentage')

    def get_positive(self, obj):
        for fr in obj.focus_regions.all():
            if fr.cancerous_region:
                return True
        return False

    @staticmethod
    def get_normal_tissue_percentage(obj):
        return obj.get_normal_tissue_percentage()


class SliceDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores = CoreSerializer(many=True, read_only=True)
    positive_cores_count = serializers.SerializerMethodField()

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'creation_date','roi_json',
                  'total_cores', 'positive_cores_count', 'cores')
        read_only_fields = ('id', 'creation_date', 'positive_cores_count')

    def get_positive_cores_count(self, obj):
        positive_cores_counter = 0
        cores = CoreSerializer(data=obj.cores.all(), many=True)
        if cores.is_valid():
            for core in cores.validated_data:
                if core.positive:
                    positive_cores_counter += 1
        return positive_cores_counter


class SlideDetailsSerializer(serializers.ModelSerializer):
    quality_control_passed = serializers.SlugRelatedField(
        read_only=True,
        slug_field='adequate_slide'
    )

    slices = SliceSerializer(many=True)

    class Meta:
        model = Slide
        fields = ('id', 'case', 'import_date', 'omero_id', 'image_type',
                  'quality_control_passed', 'image_microns_per_pixel', 'slices')
        read_only_fields = fields


class CoreROIsTreeSerializer(CoreDetailsSerializer):
    focus_regions = FocusRegionSerializer(many=True, read_only=True)


class SliceROIsTreeSerializer(SliceDetailsSerializer):
    cores = CoreROIsTreeSerializer(many=True, read_only=True)
