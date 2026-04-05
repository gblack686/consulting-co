import os, json, hashlib

aikb = "C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB"
output_dir = "C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/sync-claude-ecosystem"

type_colors = {
    "agent": ("Blue", "Knowledge and strategy"),
    "command": ("Red", "Action and execution"),
    "hook": ("Black", "Control and interception"),
    "skill": ("Green", "Growth and capability"),
    "adw": ("Gold", "Multi-color orchestration"),
    "agentic-prompt": ("White", "Order and structure"),
}

card_pools = {
    "Blue": ["Jace Beleren","Counterspell","Brainstorm","Snapcaster Mage","Force of Will","Cryptic Command","Time Walk","Ancestral Recall","Mind Sculptor","Mystic Confluence","Ponder","Serum Visions","Fact or Fiction","Mana Leak","Remand","Negate","Spell Pierce","Opt","Preordain","Think Twice","Mulldrifter","Vendilion Clique","Torrential Gearhulk","Teferi Time Raveler","Archmage Emeritus","Clever Lumimancer","Dream Trawler","Narset Parter","Venser Shaper Savant","Thassa Deep-Dwelling"],
    "Red": ["Lightning Bolt","Goblin Guide","Chandra Nalaar","Firebolt","Shock","Lava Spike","Rift Bolt","Searing Blaze","Monastery Swiftspear","Eidolon of the Great Revel","Embereth Shieldbreaker","Robber of the Rich","Bonecrusher Giant","Torbran Thane","Purphoros God","Fury","Ragavan Nimble","Dragon Rage Channeler","Unholy Heat","Abrade","Wild Slash","Searing Blood","Skullcrack","Exquisite Firecraft","Char","Flame Slash","Burst Lightning","Pillar of Flame","Roil Eruption","Play with Fire","Kumano Faces Kakkazan","Rampaging Ferocidon","Ash Zealot","Hellrider","Chandra Torch","Glorybringer","Thundermaw Hellkite","Stormbreath Dragon","Goldspan Dragon","Terror of the Peaks","Drakuseth Maw","Siege Dragon","Inferno Titan","Combustible Gearhulk","Etali Primal Storm","Flametongue Kavu","Zealous Conscripts","Kiki-Jiki Mirror","Imperial Recruiter","Dire Fleet Daredevil","Magda Brazen Outlaw","Professional Face-Breaker","Fable of Mirror-Breaker","Flame of Anor","Red Elemental Blast","Pyroblast","Blood Moon","Magus of the Moon","Through the Breach","Sneak Attack","Splinter Twin","Underworld Breach","Mizzix Mastery","Past in Flames","Grapeshot","Empty the Warrens","Goblin Bombardment","Impact Tremors","Purphoros Bronze","Cavalcade of Calamity","Light Up the Stage","Experimental Frenzy","Outpost Siege","Chandra Dressed to Kill","Reckless Impulse","Wrenn and Six","Fiery Confluence","Wheel of Fortune","Reforge the Soul","Magmatic Channeler","Young Pyromancer","Bedlam Reveler","Seasoned Pyromancer","Goblin Rabblemaster","Legion Warboss","Krenko Mob Boss","Muxus Goblin","Conspicuous Snoop","Goblin Ringleader","Goblin Matron","Skirk Prospector","Mogg War Marshal","Foundry Street Denizen","Burning-Tree Emissary","Goblin Chainwhirler","Goblin Trashmaster","Siege-Gang Commander","Pashalik Mons","Munitions Expert","Tin Street Dodger"],
    "Black": ["Dark Ritual","Thoughtseize","Fatal Push","Doom Blade","Go for the Throat","Liliana of the Veil","Phyrexian Arena","Necropotence","Demonic Tutor","Vampiric Tutor","Sheoldred Apocalypse","Grief","Dauthi Voidwalker","Tourach Dread","Sedgemoor Witch","Dark Confidant","Bloodghast","Gutterbones","Knight of Ebon","Nether Spirit","Murderous Rider","Rankle Master","Spawn of Mayhem","Doom Whisperer","Massacre Wurm","Grave Titan","Griselbrand","Razaketh Foulblooded","Vilis Broker","Archon of Cruelty","Animate Dead","Reanimate","Exhume","Living Death","Dread Return","Victimize","Buried Alive","Entomb","Cabal Therapy","Unmask","Inquisition of Kozilek","Duress","Hymn to Tourach","Mind Twist","Collective Brutality","Agonizing Remorse","Kitesail Freebooter","Brain Maggot","Mesmeric Fiend","Tidehollow Sculler","Sign in Blood","Night Whispers","Read the Bones","Village Rites","Deadly Dispute","Bone Shards","Power Word Kill","Infernal Grasp","Heartless Act"],
    "Green": ["Llanowar Elves","Birds of Paradise","Tarmogoyf","Questing Beast","Collected Company","Green Sun Zenith","Natural Order","Craterhoof Behemoth","Tooth and Nail","Primal Command","Chord of Calling","Finale of Devastation","Worldly Tutor","Sylvan Library","Tireless Tracker","Courser of Kruphix","Oracle of Mul Daya","Nissa Who Shakes","Garruk Wildspeaker","Vivien Reid","Elder Gargaroth","Thrun Last Troll","Carnage Tyrant","Primeval Titan"],
    "Gold": ["Niv-Mizzet Parun","Teferi Hero","Omnath Locus","Korvold Fae-Cursed","Atraxa Praetors Voice","Kenrith Returned King","Golos Tireless Pilgrim","Nicol Bolas Dragon-God","Maelstrom Wanderer","Muldrotha Gravetide","Yarok Desecrated","Chulane Teller","Sisay Weatherlight","Jodah Archmage"],
    "White": ["Swords to Plowshares","Path to Exile","Thalia Guardian","Elesh Norn Grand","Wrath of God","Day of Judgment","Sun Titan","Restoration Angel","Stoneforge Mystic","Monastery Mentor","Adeline Resplendent","Palace Jailer","Recruiter of Guard","Ranger-Captain Lavabrink","Solitude","Skyclave Apparition","Elite Spellbinder","Luminarch Aspirant","Esper Sentinel","Lion Sash","Cathar Commando","Isamaru Hound","Usher of Fallen","Dauntless Bodyguard","Giant Killer","Selfless Spirit","Brave the Elements","Honor of Pure","Benalish Marshal","Venerated Loxodon","Serra Ascendant","Gideon Ally","Elspeth Sun Champion","Archangel of Thune","Heliod Sun-Crowned","Speaker of Heavens","Soul Warden","Ajani Pridemate","Resplendent Angel","Lyra Dawnbringer","Baneslayer Angel","Angel of Sanctions","Angel of Invention","Archangel Avacyn","Linvala Keeper","Iona Shield","Avacyn Angel","Emeria Shepherd","Sun Blessed Guardian","Luminous Broodmoth","Seasoned Hallowblade","Alseid of Life","Charming Prince","Flickerwisp","Blade Splicer","Thraben Inspector","Spirited Companion","Brutal Cathar","Fateful Absence","Portable Hole","Glass Casket","Banishing Light","Oblivion Ring","Cast Out","Unexpectedly Absent","Council Judgment","Generous Gift","Condemn","Oust","Declaration in Stone","Seal Away","On Thin Ice","Journey to Nowhere","Fiend Hunter","Banisher Priest","Deputy of Detention"],
}

used = {c: set() for c in card_pools}

def assign_card(name, comp_type):
    color_info = type_colors.get(comp_type, ("Blue", "Default"))
    color = color_info[0]
    pool = card_pools.get(color, card_pools["Blue"])
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    idx = h % len(pool)
    attempts = 0
    while pool[idx] in used[color] and attempts < len(pool):
        idx = (idx + 1) % len(pool)
        attempts += 1
    card = pool[idx]
    used[color].add(card)
    return card, color

assignments = []
folders_to_scan = ["02-Agents", "03-Skills", "08-Commands", "09-Hooks", "01-ADWs", "10-Agentic-Prompts"]
folder_type_map = {
    "02-Agents": "agent",
    "03-Skills": "skill",
    "08-Commands": "command",
    "09-Hooks": "hook",
    "01-ADWs": "adw",
    "10-Agentic-Prompts": "agentic-prompt",
}

for folder in folders_to_scan:
    folder_path = os.path.join(aikb, folder)
    if not os.path.isdir(folder_path):
        continue
    comp_type = folder_type_map[folder]
    for f in sorted(os.listdir(folder_path)):
        if not f.endswith(".md"):
            continue
        name = f.replace(".md", "")
        card, color = assign_card(name, comp_type)
        filepath = os.path.join(folder_path, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            content = content.replace('mtg_card: ""', f'mtg_card: "{card}"')
            content = content.replace("mtg_color: \"\"", f'mtg_color: "{color}"')
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            assignments.append({"name": name, "type": comp_type, "card": card, "color": color})
        except Exception as e:
            print(f"Error: {name}: {e}")

color_stats = {}
for a in assignments:
    c = a["color"]
    color_stats[c] = color_stats.get(c, 0) + 1

with open(output_dir + "/mtg-assignments.json", "w") as f:
    json.dump({"assignments": assignments, "by_color": color_stats, "total": len(assignments)}, f, indent=2)

print(f"Total MTG cards assigned: {len(assignments)}")
for c, n in sorted(color_stats.items()):
    print(f"  {c}: {n}")
