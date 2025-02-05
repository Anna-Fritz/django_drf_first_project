from rest_framework import serializers
from market_app.models import Market, Seller


# def validate_no_x(value):
#     if 'X' in value:
#         raise serializers.ValidationError('Please No X in location')
#     return value

def validate_no_x(value):
    errors = []

    if 'X' in value:
        errors.append('Please No X in location')
    if 'Y' in value:
        errors.append('Please No Y in location')

    if errors:
        raise serializers.ValidationError(errors)

    return value


class MarketSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255, validators=[validate_no_x])
    description = serializers.CharField(max_length=255)
    net_worth = serializers.DecimalField(max_digits=100, decimal_places=2)

    def create(self, validated_data):
        return Market.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.description = validated_data.get('description', instance.description)
        instance.net_worth = validated_data.get('net_worth', instance.net_worth)
        instance.save()
        return instance

    # def validate_location(self, value):
    #     if 'X' in value:
    #         raise serializers.ValidationError('Please No X in location')
    #     return value


class SellerDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    contact_info = serializers.CharField(max_length=255)
    markets = MarketSerializer(many=True, read_only=True)


class SellerCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    contact_info = serializers.CharField(max_length=255)
    markets = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    def validate_markets(self, value):
        markets = Market.objects.filter(id__in=value)
        if len(markets) != len(value):
            raise serializers.ValidationError("One or more Market-Ids not found")
        return value

    def create(self, validated_data):
        market_ids = validated_data.pop('markets')
        seller = Seller.objects.create(**validated_data)
        markets_new = Market.objects.filter(id__in=market_ids)
        seller.markets.set(markets_new)
        return seller
