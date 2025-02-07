from rest_framework import serializers
from market_app.models import Market, Seller, Product


# def validate_no_x(value):
#     if 'X' in value:
#         raise serializers.ValidationError('Please No X in location')
#     return value

def validate_no_x(value):       # usually validation of a serializer is outsourced to a separate file, like validators.py or serializer_validators.py
    errors = []

    if 'X' in value:
        errors.append('Please No X in location')
    if 'Y' in value:
        errors.append('Please No Y in location')

    if errors:
        raise serializers.ValidationError(errors)

    return value


# MarketSerializer without ModelSerializer - Learning

# class MarketSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(max_length=255)
#     location = serializers.CharField(max_length=255, validators=[validate_no_x])
#     description = serializers.CharField(max_length=255)
#     net_worth = serializers.DecimalField(max_digits=100, decimal_places=2)

#     def create(self, validated_data):
#         return Market.objects.create(**validated_data)
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.location = validated_data.get('location', instance.location)
#         instance.description = validated_data.get('description', instance.description)
#         instance.net_worth = validated_data.get('net_worth', instance.net_worth)
#         instance.save()
#         return instance

    # def validate_location(self, value):
    #     if 'X' in value:
    #         raise serializers.ValidationError('Please No X in location')
    #     return value


class MarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Market
        fields = '__all__'


class SellerSerializer(serializers.ModelSerializer):
    markets = MarketSerializer(many=True, read_only=True)
    market_id = serializers.PrimaryKeyRelatedField(
        queryset=Market.objects.all(),
        many=True,
        write_only=True,
        source='markets'
    )

    class Meta:
        model = Seller
        exclude = []


# The SellerSerializer replaces both SellerDetailSerializer and SellerCreateSerializer \
# due to its powerful ModelSerializer options

class SellerDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    contact_info = serializers.CharField(max_length=255)
    # markets = MarketSerializer(many=True, read_only=True)
    markets = serializers.StringRelatedField(many=True)


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


class ProductDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=50, decimal_places=2)
    market = MarketSerializer(read_only=True)
    # market = serializers.StringRelatedField(read_only=True)
    seller = SellerDetailSerializer(read_only=True)


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=50, decimal_places=2)
    market_id = serializers.IntegerField(write_only=True)
    seller_id = serializers.IntegerField(write_only=True)

    def validate_market_id(self, value):
        market_id = Market.objects.filter(id=value)
        if market_id:
            return value
        else:
            raise serializers.ValidationError("Market not found")

    def validate_seller_id(self, value):
        seller_id = Seller.objects.filter(id=value)
        if seller_id:
            return value
        else:
            raise serializers.ValidationError("Seller not found")

    def create(self, validated_data):
        market_id = validated_data.pop("market_id")
        seller_id = validated_data.pop("seller_id")

        market = Market.objects.get(id=market_id)
        seller = Seller.objects.get(id=seller_id)

        product = Product.objects.create(market=market, seller=seller, **validated_data)
        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.market_id = validated_data.get('market_id', instance.market_id)
        instance.seller_id = validated_data.get('market_id', instance.seller_id)
        instance.save()
        return instance
