documents = [
    # Coffee
    {"id": "coffee_espresso", "text": """The foregoing articles make it clear that the treatment of type 2 diabetes in everyday practice
should strive to achieve the best possible control of blood glucose. This supplement underscores the inadequacies of current management in achieving this goal,
given the nature of the disease and the hesitations of physicians and patients—particularly surrounding timely initiation of intensive therapy. Yet providers should be
encouraged by the new concepts described by the authors of the articles in this supplement and others cited herein.
These concepts may advance the ability of providers to confidently manage diabetes with greater success and to provide their patients with a meaningful clinical impact 
on vascular complications."""    },
    {"id": "coffee_beans", "text": (
        "Coffee beans come primarily from two species: Arabica and Robusta. "
        "Arabica accounts for about 60 percent of world production and is "
        "prized for its smoother, more nuanced flavour. Robusta contains "
        "roughly twice as much caffeine and has a stronger, more bitter taste. "
        "Most commercial espresso blends mix the two."
    )},
    {"id": "coffee_brewing", "text": (
        "Pour-over coffee uses a filter cone to drip near-boiling water "
        "through medium-ground coffee. It typically brews for three to four "
        "minutes and produces a clean, light-bodied cup. French press coffee, "
        "in contrast, steeps coarse grounds directly in hot water for four "
        "minutes before pressing, producing a heavier, oil-rich cup."
    )},
    # Tea
    {"id": "tea_green", "text": (
        "Green tea is made from unoxidised leaves of Camellia sinensis. It is "
        "steeped in water at around 70 to 80 degrees Celsius for one to three "
        "minutes. Hotter water or longer steeping produces a bitter, astringent "
        "cup. Green tea is high in an antioxidant called EGCG."
    )},
    {"id": "tea_black", "text": (
        "Black tea comes from fully oxidised Camellia sinensis leaves. It is "
        "brewed with water at or near boiling — 95 to 100 degrees Celsius — "
        "for three to five minutes. Popular varieties include Assam, Darjeeling, "
        "and Ceylon. Black tea typically contains more caffeine than green tea."
    )},
    {"id": "tea_oolong", "text": (
        "Oolong tea is partially oxidised, sitting between green and black tea "
        "in strength and colour. It is brewed at 85 to 95 degrees Celsius for "
        "two to four minutes. Oolong leaves are often rolled and can be re-steeped "
        "several times, with each infusion revealing different flavour notes."
    )},
    # Hot chocolate
    {"id": "chocolate_traditional", "text": (
        "Traditional hot chocolate is made from melted dark chocolate stirred "
        "into hot milk. The ratio is usually 30 to 50 grams of chocolate per "
        "200 millilitres of milk. Whisking prevents the chocolate from settling. "
        "Some recipes add a pinch of chilli or cinnamon for warmth."
    )},
    {"id": "chocolate_powder", "text": (
        "Instant hot chocolate uses cocoa powder mixed with sugar, milk powder, "
        "and stabilisers. Adding hot water dissolves the mix in seconds. It is "
        "cheaper and faster than the traditional method but has a thinner mouthfeel "
        "and less intense chocolate flavour."
    )},
    {"id": "chocolate_history", "text": (
        "Hot chocolate originated with the Maya and Aztec civilisations, who "
        "drank it cold and bitter, spiced with chilli. Europeans encountered "
        "cacao in the 16th century and gradually sweetened the drink and "
        "served it hot. It remained a luxury until industrial cocoa processing "
        "made it affordable in the 19th century."
    )},
    # Milk-based drinks
    {"id": "milk_latte", "text": (
        "A caffè latte is made with one shot of espresso and around 200 "
        "millilitres of steamed milk topped with a thin layer of microfoam. "
        "The ratio is roughly one part espresso to five parts milk. A "
        "cappuccino uses the same espresso base but has equal parts milk and "
        "foam, giving it a lighter, airier texture."
    )},
]

# print(f"Loaded {len(documents)} documents.")
# for d in documents:
#     print(f"  {d['id']:25s}  {len(d['text']):3d} chars")