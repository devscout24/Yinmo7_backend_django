from django.contrib import admin

from apps.damage_analyze.models import Damage, DamageAnalyze, HumanAnalysis

# Register your models here.
@admin.register(DamageAnalyze)
class DamageAnalyzeAdmin(admin.ModelAdmin):
    list_display = ('id', 'car_owner', 'car_brand', 'car_model', 'year', 'total_estimated_min', 'total_estimated_max', 'severity')
    search_fields = ('car_brand', 'car_model', 'year')

@admin.register(Damage)
class DamageAdmin(admin.ModelAdmin):
    list_display = ('id', 'analyze', 'part_name', 'damage_type', 'damage', 'action', 'estimated_cost_min', 'estimated_cost_max')
    search_fields = ('part_name', 'damage_type', 'analyze__car_brand', 'analyze__car_model', 'analyze__year')


@admin.register(HumanAnalysis)
class HumanAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'analyze', 'created_at', 'updated_at')
    search_fields = ('analyze__car_brand', 'analyze__car_model', 'analyze__year')