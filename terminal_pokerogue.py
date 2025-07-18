import random
import time
import os

# ========== CONFIG ==========
MAX_TEAM_SIZE = 3
STARTING_POKE_COUNT = 3
STARTING_ITEMS = {"Potion": 2, "Pokeball": 3}
ITEM_EFFECTS = {
    "Potion": {"heal": 30, "desc": "Heals a Pokémon by 30 HP"},
    "Pokeball": {"capture": True, "desc": "Try to catch a wild Pokémon"}
}
TRAINER_BUFFS = {
    "Adrenaline": "10% bonus damage after using an item (resets each battle)",
    "Loyalty": "One fainted Pokémon survives once per run",
    "Sharpshooter": "+5% chance to critical hit"
}

# ========== DATA ==========
POKEMON_LIST = [
    "Pikachu", "Charmander", "Squirtle", "Bulbasaur", "Eevee", "Gengar",
    "Machop", "Psyduck", "Abra", "Snorlax", "Vulpix", "Lapras", "Growlithe"
]

MOVES = {
    "Tackle": (10, 15),
    "Bite": (8, 18),
    "Scratch": (10, 20),
    "Thunder Shock": (12, 22),
    "Ember": (10, 20),
    "Water Gun": (10, 20),
    "Vine Whip": (10, 20)
}

# ========== CLASSES ==========

class Pokemon:
    def __init__(self, name):
        self.name = name
        self.hp = random.randint(40, 70)
        self.max_hp = self.hp
        self.moves = random.sample(list(MOVES.items()), 2)
        self.alive = True
        self.used_loyalty = False

    def take_damage(self, dmg, trainer_buff, used_item_this_battle):
        if trainer_buff == "Adrenaline" and used_item_this_battle:
            dmg = int(dmg * 1.1)
        if trainer_buff == "Sharpshooter" and random.random() < 0.05:
            print("💥 Critical hit!")
            dmg *= 2
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount):
        if self.alive:
            self.hp = min(self.max_hp, self.hp + amount)

    def revive_loyalty(self, trainer_buff):
        if not self.alive and trainer_buff == "Loyalty" and not self.used_loyalty:
            self.hp = self.max_hp // 2
            self.alive = True
            self.used_loyalty = True
            print(f"❤️ {self.name}'s loyalty brought them back to life!")
            return True
        return False

class Player:
    def __init__(self, mode, trainer_buff):
        self.team = []
        self.box = []
        self.items = dict(STARTING_ITEMS)
        self.mode = mode
        self.buff = trainer_buff
        self.used_item_this_battle = False

    def generate_team(self, count):
        self.team = [Pokemon(random.choice(POKEMON_LIST)) for _ in range(count)]

    def add_pokemon(self, pkmn):
        if len(self.team) < MAX_TEAM_SIZE:
            self.team.append(pkmn)
            print(f"✅ {pkmn.name} added to your team!")
        else:
            self.box.append(pkmn)
            print(f"📦 {pkmn.name} sent to your PC (team full).")

    def has_alive_pokemon(self):
        return any(p.alive for p in self.team)

    def get_alive_pokemon(self):
        return [p for p in self.team if p.alive]

# ========== HELPERS ==========

def clear(): os.system("clear" if os.name == "posix" else "cls")
def pause(): input("Press Enter to continue...")

def choose_trainer_buff():
    print("🎖️ Choose a Trainer Buff:")
    for i, (buff, desc) in enumerate(TRAINER_BUFFS.items(), 1):
        print(f"{i}. {buff} - {desc}")
    while True:
        c = input("Enter number: ")
        if c in map(str, range(1, len(TRAINER_BUFFS)+1)):
            return list(TRAINER_BUFFS.keys())[int(c)-1]

def select_mode():
    print("""Select a game mode:
1. Normal
2. Hardcore (permadeath)
3. Random Team Every Battle""")
    while True:
        m = input("Enter mode: ")
        if m in ["1", "2", "3"]:
            return ["normal", "hardcore", "random"][int(m)-1]

def print_team(team):
    for i, p in enumerate(team, 1):
        status = "🟢" if p.alive else "🔴"
        print(f"{i}. {p.name} - {p.hp}/{p.max_hp} HP {status}")
def battle(player: Player, round_num: int):
    clear()
    print(f"⚔️ BATTLE {round_num}")
    wild = Pokemon(random.choice(POKEMON_LIST))
    print(f"A wild {wild.name} appeared! HP: {wild.hp}")
    pause()

    while wild.alive and player.has_alive_pokemon():
        clear()
        print(f"🌟 Your Team:")
        print_team(player.team)
        print(f"\n🎯 Wild {wild.name} - {wild.hp} HP")
        print("\nOptions:\n1. Attack\n2. Use Item\n3. Throw Pokéball")
        choice = input("Choose an action: ")
        if choice == "1":
            attacker = choose_own_pokemon(player)
            move_name, move_dmg = choose_move(attacker)
            print(f"Your {attacker.name} used {move_name}!")
            wild.take_damage(random.randint(*move_dmg), player.buff, player.used_item_this_battle)
        elif choice == "2":
            use_item(player)
            player.used_item_this_battle = True
        elif choice == "3":
            success = try_catch(wild, player)
            if success:
                return
        else:
            print("Invalid input.")
            continue

        if wild.alive:
            defender = random.choice(player.get_alive_pokemon())
            move = random.choice(wild.moves)
            print(f"{wild.name} used {move[0]} on your {defender.name}!")
            defender.take_damage(random.randint(*move[1]), "", False)
            if not defender.alive:
                print(f"💀 {defender.name} fainted!")
                revived = defender.revive_loyalty(player.buff)
                if not revived and player.mode == "hardcore":
                    player.team.remove(defender)
        pause()

def choose_own_pokemon(player):
    while True:
        print("\nChoose your Pokémon:")
        for i, p in enumerate(player.team, 1):
            if p.alive:
                print(f"{i}. {p.name} ({p.hp}/{p.max_hp} HP)")
        c = input("Pick #: ")
        if c.isdigit() and int(c)-1 in range(len(player.team)):
            chosen = player.team[int(c)-1]
            if chosen.alive:
                return chosen

def choose_move(pokemon):
    print(f"\n{pokemon.name}'s Moves:")
    for i, (name, dmg) in enumerate(pokemon.moves, 1):
        print(f"{i}. {name} ({dmg[0]}-{dmg[1]} dmg)")
    while True:
        c = input("Pick move #: ")
        if c in ["1", "2"]:
            return pokemon.moves[int(c)-1]

def use_item(player):
    if not player.items:
        print("Your bag is empty.")
        return
    print("\n🎒 Bag:")
    for i, (item, qty) in enumerate(player.items.items(), 1):
        print(f"{i}. {item} x{qty} - {ITEM_EFFECTS[item]['desc']}")
    c = input("Choose item #: ")
    if not c.isdigit() or int(c)-1 not in range(len(player.items)):
        print("Invalid.")
        return
    item = list(player.items.keys())[int(c)-1]
    if item == "Potion":
        poke = choose_own_pokemon(player)
        poke.heal(ITEM_EFFECTS[item]["heal"])
        print(f"{poke.name} healed!")
    player.items[item] -= 1
    if player.items[item] <= 0:
        del player.items[item]

def try_catch(wild, player):
    if "Pokeball" not in player.items:
        print("No Pokéballs left!")
        return False
    chance = wild.hp / wild.max_hp
    print("🎯 You threw a Pokéball!")
    time.sleep(1)
    if random.random() > chance:
        print(f"✅ You caught {wild.name}!")
        player.add_pokemon(wild)
        return True
    else:
        print("❌ The Pokémon broke free!")
        player.items["Pokeball"] -= 1
        if player.items["Pokeball"] <= 0:
            del player.items["Pokeball"]
        return False

# ========== MAIN GAME LOOP ==========

def main():
    clear()
    print("🧢 Welcome to Terminal PokéRogue!")
    mode = select_mode()
    buff = choose_trainer_buff()
    player = Player(mode, buff)

    round_num = 1
    while True:
        player.used_item_this_battle = False
        if mode == "random":
            player.generate_team(STARTING_POKE_COUNT)
        elif round_num == 1:
            player.generate_team(STARTING_POKE_COUNT)

        if not player.has_alive_pokemon():
            print("All your Pokémon have fainted. Game over.")
            return

        battle(player, round_num)
        round_num += 1

main()
