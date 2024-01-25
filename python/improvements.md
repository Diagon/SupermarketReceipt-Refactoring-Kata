# Overview


Current code for discount handling looks like incremental adhoc approach and generalization is due.
Moreover, if we plan to change rules weakly it is better to store them as a data rather than edit the code to avoid further deterioration.

## Offers

To generalize handling multiple types of offers we can create simple rules engine.
To store offer, at minimum, we would need to know what products it is applicable to & how that would change pricing.

### Offer pricing formulas

For the given requirements we have 3 scenarios:   
- N of the good for X percent discount
  - e.g. "20% discount on apples" when N=1
  - e.g. "20% discount on apples if bought over 2kg" when N>1
- N of the good for the fixed price 
  - e.g. "Five tubes of toothpaste for €7.49"
- Buy N of the good, get M of the good for free 
  - e.g. "Buy two toothbrushes, get one free"


Therefore, to define & store offer at minimum we need:
- applicability criteria that includes products & amount
- type & size of effect on price
  - Price effect in general case is simple:
    - ```price = (quantity - freebies) * (price * discount)```
    - we can pass required values as arguments for each specific offer


Then algorithm to calculate total price would be as simple as to iterate through the items in the shopping basket and apply offer for the given product.

Note here, that in case of multiple offers for the same product we don't have solid requirements, so collision is possible. We will talk about this later.

## Going deeper

This would have been enough to generalize current implementation, but it wouldn't cover new suggested feature: discounted bundles.

Elegant way to refactor the code to handle bundles as well as all the previous use cases is to change applicability criteria to handle lists of goods as a trigger for an offer rather than singe good. Bundles will be represented with multiple product/amoubnt pairs and all previous scenarios are simply triggered with the bundles with 1 element inside.

In the end this is how offer can be defined with following pseudocode: 
```
Offer(
    name="Fruit bundle", 
    trigger=[
        ProductQuantity(apple, 1),
        ProductQuantity(banana, 1),
        ProductQuantity(orange, 1),
    ],
    effect=("fixed_price", 1.99)
)
```

Final algorithm can be represented with the following pseudocode:
```
# handle offers
for offer in offers:
    if applicable_goods_are_in_basket(offer, basket):
        handle_item(offer) 
        remove_from_basket(offer, basket)

# Handle the rest of the goods, which are not applicable to any offer 
for item in basket:
    handle_item(offer)
```

### Overlapping offers

Previously mentioned, we can have a multiple contradicting offers applicable to given basket.
Requirements do not specify what is expected behaviour in that case. 

We can assume two scenarios:

First option is to have predetermined priority, e.g. weight for each over or simply use the first applicable offer.  

Second option is to find optimal offer combination for a given basket, minimizing the cost.
However, this is going to be a variation of **knapsack problem**, which is **NP-hard** problem and has no known efficient solution. 
Best bet would be to use something like dynamic programming approach, but it will struggle with large basket sizes anyway.   

## Receipt printer

Given new requirement for HTML receipt, it makes sense to rewrite receipt printer into interface for printing; 
Then we can have multiple implementations for various mediums like string or HTML output.  
