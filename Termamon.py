import sys
import random
import os

def _win_compat():
    if os.name == "nt":
        try:
            import colorama
            colorama.just_fix_windows_console()
        except Exception:
            pass
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass


MOVE_DB = {
    "Ember": {"power": 35, "type": "Fire"},
    "Scratch": {"power": 30, "type": "Normal"},
    "Flamethrower": {"power": 90, "type": "Fire"},
    "Water Gun": {"power": 40, "type": "Water"},
    "Tackle": {"power": 30, "type": "Normal"},
    "Bubble": {"power": 30, "type": "Water"},
    "Vine Whip": {"power": 45, "type": "Grass"},
    "Razor Leaf": {"power": 55, "type": "Grass"},
    "Thunder Shock": {"power": 40, "type": "Electric"},
    "Quick Attack": {"power": 40, "type": "Normal"},
    "Thunderbolt": {"power": 90, "type": "Electric"},
    "Rock Throw": {"power": 50, "type": "Rock"},
    "Magnitude": {"power": 70, "type": "Ground"},
    "Lick": {"power": 30, "type": "Ghost"},
    "Night Shade": {"power": 50, "type": "Ghost"},
    "Hypnosis": {"power": 0, "type": "Psychic"},
    "Bite": {"power": 60, "type": "Dark"},
    "Flame Wheel": {"power": 60, "type": "Fire"},
    "Body Slam": {"power": 85, "type": "Normal"},
    "Supersonic": {"power": 0, "type": "Normal"},
    "Absorb": {"power": 20, "type": "Grass"},
    "Acid": {"power": 40, "type": "Poison"},
    "Stun Spore": {"power": 0, "type": "Grass"},
}

POKEMON_ROSTER = [
    {"name": "Charmander", "type": "Fire", "moves": ["Ember", "Scratch", "Flamethrower"], "max_hp": 39},
    {"name": "Squirtle", "type": "Water", "moves": ["Water Gun", "Tackle", "Bubble"], "max_hp": 44},
    {"name": "Bulbasaur", "type": "Grass", "moves": ["Vine Whip", "Tackle", "Razor Leaf"], "max_hp": 45},
    {"name": "Pikachu", "type": "Electric", "moves": ["Thunder Shock", "Quick Attack", "Thunderbolt"], "max_hp": 35},
    {"name": "Geodude", "type": "Rock", "moves": ["Rock Throw", "Tackle", "Magnitude"], "max_hp": 40},
    {"name": "Gastly", "type": "Ghost", "moves": ["Lick", "Night Shade", "Hypnosis"], "max_hp": 30},
    {"name": "Growlithe", "type": "Fire", "moves": ["Ember", "Bite", "Flame Wheel"], "max_hp": 55},
    {"name": "Poliwag", "type": "Water", "moves": ["Water Gun", "Bubble", "Body Slam"], "max_hp": 40},
    {"name": "Magnemite", "type": "Electric", "moves": ["Thunder Shock", "Tackle", "Supersonic"], "max_hp": 25},
    {"name": "Oddish", "type": "Grass", "moves": ["Absorb", "Acid", "Stun Spore"], "max_hp": 45},
]

TRAINERS = [
    {"name": "Ash", "buff": "Pokéballs +2 in Speedrunner"},
    {"name": "Misty", "buff": "Water Pokémon HP +10 in Survivor"},
    {"name": "Brock", "buff": "Rock Pokémon Defense +5 in Survivor"},
    {"name": "No Trainer", "buff": None}
]

TRAINER_BUFFS = {
    "Speedrunner": [
        {"trainer": "Ash", "buff": "Pokéballs +2"},
    ],
    "Survivor": [
        {"trainer": "Misty", "buff": "Water Pokémon HP +10"},
        {"trainer": "Brock", "buff": "Rock Pokémon Defense +5"},
    ],
    "Normal": []
}

GAMEMODES = ["Normal", "Speedrunner", "Survivor"]
MAX_PARTY_SIZE = 6

class PokemonInstance:
    def __init__(self, base):
        self.name = base["name"]
        self.type = base["type"]
        self.moves = base["moves"]
        self.max_hp = base["max_hp"]
        self.hp = self.max_hp

    def heal(self):
        self.hp = self.max_hp

    def __str__(self):
        return f"{self.name} (Type: {self.type}, HP: {self.hp}/{self.max_hp})"

class GameState:
    def __init__(self):
        self.trainer = None
        self.gamemode = None
        self.party = []
        self.pokeballs = 5
        self.active_idx = 0
        self.starter_chosen = False

    def reset(self):
        self.trainer = None
               self.gamemode = None
        self.party = []
        self.pokeballs = 5
        self.active_idx = 0
        self.starter_chosen = False

    def add_to_party(self, poke):
        if len(self.party) < MAX_PARTY_SIZE and not any(p.name == poke.name for p in self.party):
            self.party.append(poke)
        elif any(p.name == poke.name for p in self.party):
            print(f"{poke.name} is already in your party!")
        else:
            print("Your party is full! (Max 6 Pokémon)")

    def switch_active(self, idx):
        if 0 <= idx < len(self.party):
            self.active_idx = idx
        else:
            print("Invalid party slot.")

    def get_active(self):
        if self.party:
            return self.party[self.active_idx]
        return None

def print_menu(options, add_back=True, add_exit=True):
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    idx = len(options)
    if add_back:
        print(f"{idx+1}. Back")
        idx += 1
    if add_exit:
        print(f"{idx+1}. Exit")

def wait_input(options, add_back=True, add_exit=True):
    print_menu(options, add_back, add_exit)
    valid = list(range(1, len(options)+1))
    back_idx = len(options)+1 if add_back else None
    exit_idx = len(options)+2 if add_back and add_exit else len(options)+1 if add_exit else None
    while True:
        choice = input("Choose an option: ")
        if choice.isdigit():
            idx = int(choice)
            if idx in valid:
                return idx - 1
            elif add_back and idx == back_idx:
                return "back"
            elif add_exit and idx == exit_idx:
                print("Goodbye!")
                sys.exit()
        print("Invalid choice.")

def main_menu(game):
    while True:
        print("\nMain Menu:")
        options = ["Start Game", "Options", "View Roster", "View Party", "Heal Party"]
        sel = wait_input(options, add_back=False)
        if sel == 0:
            start_game(game)
        elif sel == 1:
            options_menu(game)
        elif sel == 2:
            show_roster()
        elif sel == 3:
            show_party(game)
        elif sel == 4:
            heal_party(game)

def options_menu(game):
    while True:
        print("\nOptions:")
        options = ["Select Trainer", "Select Gamemode"]
        sel = wait_input(options)
        if sel == 0:
            select_trainer(game)
        elif sel == 1:
            select_gamemode(game)
        elif sel == "back":
            return

def select_trainer(game):
    while True:
        print("\nSelect Trainer:")
        options = [t["name"] for t in TRAINERS]
        sel = wait_input(options)
        if sel == "back":
            return
        game.trainer = TRAINERS[sel]["name"]
        print(f"Selected Trainer: {game.trainer}")
        return

def select_gamemode(game):
    while True:
        print("\nSelect Gamemode:")
        options = GAMEMODES
        sel = wait_input(options)
        if sel == "back":
            return
        game.gamemode = GAMEMODES[sel]
        print(f"Selected Gamemode: {game.gamemode}")
        buffs = [b for b in TRAINER_BUFFS[game.gamemode] if b["trainer"] == game.trainer]
        if buffs:
            print(f"Trainer Buff: {buffs[0]['buff']}")
        elif game.trainer == "No Trainer":
            print("No trainer selected, no buffs.")
        else:
            print("No applicable trainer buffs in this mode.")
        return

def show_roster():
    print("\nAvailable Pokémon:")
    for i, poke in enumerate(POKEMON_ROSTER):
        print(f"{i+1}. {poke['name']} (Type: {poke['type']}, HP: {poke['max_hp']}, Moves: {', '.join(poke['moves'])})")

def show_party(game):
    print("\nYour Pokémon Party:")
    if not game.party:
        print("You have no Pokémon. Catch some!")
    else:
        for i, poke in enumerate(game.party):
            active_str = " (ACTIVE)" if i == game.active_idx else ""
            print(f"{i+1}. {poke.name} (Type: {poke.type}, HP: {poke.hp}/{poke.max_hp}){active_str}")
    print(f"Pokéballs: {game.pokeballs}")
    options = []
    _ = wait_input(options)  

def heal_party(game):
    for poke in game.party:
        poke.heal()
    print("All party Pokémon healed!")

def pick_starters(game):
    print("\nPick your 3 starter Pokémon from the roster:")
    chosen = []
    available_indices = list(range(len(POKEMON_ROSTER)))
    while len(chosen) < 3:
        print("\nAvailable Pokémon:")
        for display_idx, poke_idx in enumerate(available_indices):
            poke = POKEMON_ROSTER[poke_idx]
            print(f"{display_idx+1}. {poke['name']} (Type: {poke['type']}, HP: {poke['max_hp']}, Moves: {', '.join(poke['moves'])})")
        sel = input(f"Pick Pokémon #{len(chosen)+1} (enter number): ")
        if sel.isdigit():
            pick_display_idx = int(sel)-1
            if 0 <= pick_display_idx < len(available_indices):
                pick_idx = available_indices[pick_display_idx]
                chosen.append(PokemonInstance(POKEMON_ROSTER[pick_idx]))
                available_indices.remove(pick_idx)
            else:
                print("Invalid selection or already picked.")
        else:
            print("Enter a valid number.")
    for poke in chosen:
        game.add_to_party(poke)
    print("Starter Pokémon chosen!")
    game.starter_chosen = True
    game.active_idx = 0

def start_game(game):
    if game.trainer is None:
        print("Select a trainer first in Options!")
        return
    if game.gamemode is None:
        print("Select a gamemode first in Options!")
        return
    if not game.starter_chosen:
        pick_starters(game)
    print("\nStarting your adventure!")
    if game.trainer != "No Trainer" and game.gamemode in TRAINER_BUFFS:
        for buff in TRAINER_BUFFS[game.gamemode]:
            if buff["trainer"] == game.trainer:
                if "Pokéballs +2" in buff["buff"]:
                    game.pokeballs += 2
    while True:
        encounter_menu(game)
        print("\nWhat do you want to do next?")
        options = ["Continue Adventure"]
        sel = wait_input(options)
        if sel == "back":
            break

def encounter_menu(game):
    wild_base = random.choice(POKEMON_ROSTER)
    wild_pokemon = PokemonInstance(wild_base)
    print(f"\nA wild {wild_pokemon.name} appeared!")
    print(f"Type: {wild_pokemon.type}, HP: {wild_pokemon.hp}/{wild_pokemon.max_hp}")
    print(f"Moves: {', '.join(wild_pokemon.moves)}")
    while wild_pokemon.hp > 0:
        options = ["Attack", "Throw Pokéball", "Run Away", "Switch Pokémon"]
        sel = wait_input(options)
        if sel == 0:  
            player_attack(game, wild_pokemon)
            if wild_pokemon.hp <= 0:
                print(f"{wild_pokemon.name} fainted! You can't catch it now.")
                return
        elif sel == 1:  
            if game.pokeballs <= 0:
                print("You are out of Pokéballs!")
                continue
            game.pokeballs -= 1
            catch_rate = 0.7 * (wild_pokemon.hp / wild_pokemon.max_hp)
            if game.trainer == "Misty" and game.gamemode == "Survivor" and wild_pokemon.type == "Water":
                catch_rate += 0.15
            if random.random() < catch_rate:
                print(f"You caught {wild_pokemon.name}!")
                game.add_to_party(PokemonInstance(wild_base))
                return
            else:
                print("Oh no! The Pokémon escaped.")
        elif sel == 2:  
            print("You ran away safely.")
            return
        elif sel == 3:  
            switch_pokemon(game)
        elif sel == "back":
            return

def player_attack(game, wild_pokemon):
    active_poke = game.get_active()
    if not active_poke:
        print("You have no Pokémon to attack with!")
        return
    print(f"\nChoose a move to attack with {active_poke.name}:")
    move_specs = []
    for move in active_poke.moves:
        specs = MOVE_DB.get(move, {})
        move_type = specs.get("type", "Unknown")
        move_power = specs.get("power", "Unknown")
        move_specs.append(f"{move} (Type: {move_type}, Power: {move_power})")
    sel = wait_input(move_specs)
    if sel == "back":
        return
    move_name = active_poke.moves[sel]
    move_power = MOVE_DB[move_name]["power"]
    dmg = random.randint(int(move_power*0.7), move_power)
    wild_pokemon.hp = max(0, wild_pokemon.hp - dmg)
    print(f"{active_poke.name} used {move_name}! It dealt {dmg} damage.")
    print(f"{wild_pokemon.name}'s HP: {wild_pokemon.hp}/{wild_pokemon.max_hp}")

def switch_pokemon(game):
    if not game.party:
        print("No Pokémon to switch!")
        return
    print("\nChoose Pokémon to make active:")
    options = []
    for i, poke in enumerate(game.party):
        active_str = " (ACTIVE)" if i == game.active_idx else ""
        options.append(f"{poke.name} (Type: {poke.type}, HP: {poke.hp}/{poke.max_hp}){active_str}")
    sel = wait_input(options, add_back=True, add_exit=True)
    if sel == "back":
        return
    if 0 <= sel < len(game.party):
        game.switch_active(sel)
        print(f"{game.party[game.active_idx].name} is now active!")
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    _win_compat() 
    game = GameState()
    main_menu(game)
