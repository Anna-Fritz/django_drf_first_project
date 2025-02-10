from rest_framework import serializers
from market_app.models import Market, Seller, Product
from django.urls import reverse


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



# HyperlinkedRelatedField

class MarketSerializer(serializers.ModelSerializer):

    sellers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='seller_single')

    class Meta:
        model = Market
        fields = '__all__'


class MarketHyperlinkedSerializer(MarketSerializer, serializers.HyperlinkedModelSerializer):
    sellers = None

    """
    modifying fields dynamically
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    displayed fields have to be defined in markets_view while creating MarketHyperlinkedSerializer
    """

    # def __init__(self, *args, **kwargs):
    #     # Don't pass the 'fields' arg up to the superclass
    #     fields = kwargs.pop('fields', None)

    #     # Instantiate the superclass normally
    #     super().__init__(*args, **kwargs)

    #     if fields is not None:
    #         # Drop any fields that are not specified in the `fields` argument.
    #         allowed = set(fields)
    #         existing = set(self.fields)
    #         for field_name in existing - allowed:
    #             self.fields.pop(field_name)

    class Meta:
        model = Market
        fields = ['id', 'name', 'url', 'location', 'description', 'net_worth']




# HyperlinkedModelSerializer: generates url key-value for each model automaticly, needs naming (name='name-detail') for url-path
# and context={'request': request} as argument for Serializer in related view

# class MarketSerializer(serializers.HyperlinkedModelSerializer):

#     sellers = serializers.StringRelatedField(many=True, read_only=True)

#     class Meta:
#         model = Market
#         fields = ['name', 'url', 'location', 'description', 'net_worth', 'sellers']



# Additional solution for using Hyperlinks, but also rendering their names

# class MarketSerializer(serializers.ModelSerializer):

#     sellers = serializers.SerializerMethodField()

#     class Meta:
#         model = Market
#         fields = ['id', 'sellers', 'name', 'location', 'description', 'net_worth']

#     def get_sellers(self, obj):
#         """Returns seller names as clickable links."""
#         request = self.context.get('request')  # Request-Objekt für absolute URLs
#         return [
#             {
#                 "name": seller.name,
#                 "url": request.build_absolute_uri(reverse("seller_single", args=[seller.id]))
#             }
#             for seller in obj.sellers.all()
#         ]



# this MarketSerializer allows hyperlinked Name in Frontend:

# class MarketSerializer(serializers.ModelSerializer):

#     sellers = serializers.SerializerMethodField()

#     class Meta:
#         model = Market
#         fields = '__all__'

#     def get_sellers(self, obj):
#         request = self.context.get('request')  # Request-Objekt for absolute URLs
#         return [
#             f'<a href="{request.build_absolute_uri(reverse("seller_single", args=[seller.id]))}">{seller.name}</a>'
#             for seller in obj.sellers.all()
#         ]


class SellerSerializer(serializers.ModelSerializer):
    markets = MarketSerializer(many=True, read_only=True)
    market_id = serializers.PrimaryKeyRelatedField(
        queryset=Market.objects.all(),
        many=True,
        write_only=True,
        source='markets'
    )

    market_count = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = ['id', 'name', 'market_id', 'market_count', 'markets', 'contact_info']

    def get_market_count(self, obj):
        return obj.markets.count()


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


class ProductSerializer(serializers.ModelSerializer):
    market = serializers.StringRelatedField()
    seller = serializers.StringRelatedField()

    # only name of market & seller
    # market = serializers.StringRelatedField()
    # seller = serializers.StringRelatedField()

    # all model information of market & seller
    # market = MarketSerializer(read_only=True)
    # seller = SellerSerializer(read_only=True)

    market_id = serializers.PrimaryKeyRelatedField(
        queryset=Market.objects.all(),
        write_only=True,
        source='market'
    )
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=Seller.objects.all(),
        write_only=True,
        source='seller'
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'market', 'seller', 'market_id', 'seller_id']

    # def get_seller(self, obj):
    #     request = self.context.get('request')  # Request-Objekt for absolute URLs
    #     return [
    #         f'<a href="{request.build_absolute_uri(reverse("seller_single", args=[seller.id]))}">{seller.name}</a>'
    #         for seller in obj.seller.all()
    #     ]
    
    # def get_market(self, obj):
    #     request = self.context.get('request')  # Request-Objekt for absolute URLs
    #     return [
    #         f'<a href="{request.build_absolute_uri(reverse("market-detail", args=[market.id]))}">{market.name}</a>'
    #         for market in obj.market.all()
    #     ]


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
