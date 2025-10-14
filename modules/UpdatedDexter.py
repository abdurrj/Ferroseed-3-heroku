# UpdatedDexter.py
import aiohttp
import discord
from discord.ext import commands
from typing import Dict, List, Optional, Tuple

POKEAPI_POKEMON = "https://pokeapi.co/api/v2/pokemon/{key}/"
POKEAPI_SPECIES = "https://pokeapi.co/api/v2/pokemon-species/{id}/"

POKEMONDB_HOME = "https://img.pokemondb.net/sprites/home"

# -----------------------------------------------------------------------------
# Small helpers
# -----------------------------------------------------------------------------

def _title(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s

_SPECIAL_DISPLAY_MAP = {
    "mr-mime": "Mr. Mime",
    "mr-rime": "Mr. Rime",
    "mime-jr": "Mime Jr.",
    "type-null": "Type: Null",
    "farfetchd": "Farfetch’d",
    "sirfetchd": "Sirfetch’d",
    "ho-oh": "Ho-Oh",
    "jangmo-o": "Jangmo-o",
    "hakamo-o": "Hakamo-o",
    "kommo-o": "Kommo-o",
    "porygon-z": "Porygon-Z",
    "flabebe": "Flabébé",
}

def slug_to_display(slug: str) -> str:
    s = slug.lower()
    if s in _SPECIAL_DISPLAY_MAP:
        return _SPECIAL_DISPLAY_MAP[s]
    return _title(s.replace("-", " "))

def types_display(types_obj: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    s = sorted(types_obj, key=lambda t: t["slot"])
    t1 = _title(s[0]["type"]["name"]) if s else None
    t2 = _title(s[1]["type"]["name"]) if len(s) > 1 else None
    return t1, t2

def abilities_to_named(abilities_arr: List[Dict]) -> Dict[str, Optional[str]]:
    a1 = a2 = ah = None
    for item in abilities_arr:
        name = item["ability"]["name"].replace("-", " ").title()
        if item["is_hidden"]:
            ah = name
        else:
            if item["slot"] == 1:
                a1 = name
            elif item["slot"] == 2:
                a2 = name
    return {"ability1": a1, "ability2": a2, "abilityH": ah}

def is_shiny_requested(form_input: Tuple[str, ...]) -> bool:
    lowered = [x.lower() for x in form_input]
    return ("shiny" in lowered) or ("*" in lowered)

def normalize_key(s: str) -> str:
    return s.lower().replace(".", "-").replace("_", "-").replace(" ", "-")

def pokemon_db_slug_from_pokeapi_slug(slug: str) -> str:
    """
    Convert PokeAPI variety slug to PokemonDB HOME sprite slug.
    Handles regional forms, G-Max, Deoxys, and Tauros (Paldea) breeds.
    """
    s = slug

    # --- Special cases FIRST ---
    # Tauros (Paldea) breeds:
    # PokeAPI: tauros-paldea-combat-breed / -blaze-breed / -aqua-breed
    # PokemonDB: tauros-paldean-combat / -paldean-fire / -paldean-aqua
    if s.startswith("tauros-paldea-"):
        if s.endswith("aqua-breed"):
            return "tauros-paldean-aqua"
        if s.endswith("blaze-breed"):
            return "tauros-paldean-blaze"
        if s.endswith("combat-breed"):
            return "tauros-paldean-combat"

    # Deoxys: normal form on PokemonDB is just "deoxys"
    if s == "deoxys-normal":
        return "deoxys"

    # --- Generic mappings ---
    s = s.replace("-galar", "-galarian")
    s = s.replace("-alola", "-alolan")
    s = s.replace("-hisui", "-hisuian")
    s = s.replace("-paldea", "-paldean")   # general Paldean mapping
    s = s.replace("-gmax", "-gigantamax")

    return s

def sprite_url(name_slug: str, shiny: bool) -> str:
    folder = "shiny" if shiny else "normal"
    db_slug = pokemon_db_slug_from_pokeapi_slug(name_slug)
    return f"{POKEMONDB_HOME}/{folder}/{db_slug}.png"

def mega_display_tokens(variety_slug: str) -> Optional[str]:
    s = variety_slug.lower()
    if "-mega-x" in s:
        return "Mega X"
    if "-mega-y" in s:
        return "Mega Y"
    if s.endswith("-mega") or "-mega-" in s:
        return "Mega"
    return None

def form_label_from_variety(slug: str) -> Optional[str]:
    s = slug.lower()
    if "-gmax" in s or "gigantamax" in s:
        return "Gigantamax"
    if "alola" in s:
        return "Alolan"
    if "galar" in s:
        return "Galarian"
    if "hisui" in s:
        return "Hisuian"
    if "paldea" in s:
        if "aqua" in s:
            return "Paldean Water"
        if "blaze" in s:
            return "Paldean Fire"
        return "Paldean"
    return None

# Detect requested forms (regional/G-Max + Deoxys aspects)
def requested_form_suffix(form_input: Tuple[str, ...], base_key: str) -> Optional[str]:
    """
    Returns a PokeAPI suffix like:
      -galar, -alola, -hisui, -paldea, -paldea-aqua-breed, -paldea-blaze-breed, -paldea-combat-breed, -gmax
    Also handles Deoxys aspects: -normal, -attack, -defense, -speed
    """
    toks = [t.lower() for t in form_input]
    joined = " ".join(toks)

    # Deoxys aspects
    if base_key == "deoxys":
        if "normal" in toks:  return "-normal"
        if "attack" in toks:  return "-attack"
        if "defense" in toks or "defence" in toks: return "-defense"
        if "speed" in toks:   return "-speed"

    # Gigantamax
    if "gmax" in toks or "gigantamax" in toks:
        return "-gmax"

    # Regional generics
    if "galar" in toks or "galarian" in toks:
        return "-galar"
    if "alola" in toks or "alolan" in toks:
        return "-alola"
    if "hisui" in toks or "hisuian" in toks:
        return "-hisui"

    # Paldea (generic + Tauros breeds)
    if "paldea" in toks or "paldean" in toks or "paldea" in joined or "paldean" in joined:
        if base_key == "tauros":
            if "water" in toks or "paldean water" in joined or "water" in joined:
                return "-paldea-aqua-breed"
            if "fire" in toks or "paldean fire" in joined or "fire" in joined:
                return "-paldea-blaze-breed"
            # plain ".dex tauros paldean"
            return "-paldea-combat-breed"
        # other species like Wooper
        return "-paldea"

    return None

def requested_mega_suffix(form_input: Tuple[str, ...]) -> Optional[str]:
    """
    Returns '-mega', '-mega-x', or '-mega-y' when detected.
    """
    toks = [t.lower() for t in form_input]
    joined = "-".join(toks)
    if any(t in {"mega-x", "megax"} for t in toks) or "mega-x" in joined:
        return "-mega-x"
    if any(t in {"mega-y", "megay"} for t in toks) or "mega-y" in joined:
        return "-mega-y"
    if "mega" in toks or "mega" in joined:
        return "-mega"
    return None

def nice_mega_title(base_display: str, slug: str) -> str:
    if slug.endswith("-mega-x"):
        return f"Mega {base_display} X"
    if slug.endswith("-mega-y"):
        return f"Mega {base_display} Y"
    if slug.endswith("-mega"):
        return f"Mega {base_display}"
    return base_display

# -----------------------------------------------------------------------------
# Caching + HTTP
# -----------------------------------------------------------------------------

class _Cache:
    def __init__(self):
        self.pokemon: Dict[str, dict] = {}
        self.species: Dict[int, dict] = {}
        self.species_by_url: Dict[str, dict] = {}
        self.evo: Dict[str, dict] = {}

CACHE = _Cache()

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Optional[dict]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                return await r.json()
    except Exception:
        return None
    return None

async def get_pokemon(session: aiohttp.ClientSession, key: str) -> Optional[dict]:
    """
    Robust Pokémon fetcher:
      1) Try /pokemon/{key}
      2) If that fails, try species -> default variety
      3) Cache by normalized key and by ID
    """
    k = normalize_key(key)
    if k in CACHE.pokemon:
        return CACHE.pokemon[k]

    # 1) direct pokemon
    data = await fetch_json(session, POKEAPI_POKEMON.format(key=k))
    if not data and k != key:
        data = await fetch_json(session, POKEAPI_POKEMON.format(key=key))

    # 2) fallback: species -> default variety pokemon
    if not data:
        # species can be addressed by slug or numeric id
        species = await fetch_json(session, POKEAPI_SPECIES.format(id=k))
        if not species and k != key:
            species = await fetch_json(session, POKEAPI_SPECIES.format(id=key))
        if species:
            default_var = next((v for v in species.get("varieties", []) if v.get("is_default")), None)
            if default_var:
                # most robust: follow the provided pokemon URL
                data = await fetch_json(session, default_var["pokemon"]["url"])

    if data:
        CACHE.pokemon[k] = data
        CACHE.pokemon[str(data["id"])] = data  # also cache by ID
    return data

async def get_species_by_id(session: aiohttp.ClientSession, dex_id: int) -> Optional[dict]:
    if dex_id in CACHE.species:
        return CACHE.species[dex_id]
    data = await fetch_json(session, POKEAPI_SPECIES.format(id=dex_id))
    if data:
        CACHE.species[dex_id] = data
    return data

async def get_species_by_url(session: aiohttp.ClientSession, url: str) -> Optional[dict]:
    if url in CACHE.species_by_url:
        return CACHE.species_by_url[url]
    data = await fetch_json(session, url)
    if data:
        CACHE.species_by_url[url] = data
        CACHE.species[data["id"]] = data
    return data

async def get_evolution_chain(session: aiohttp.ClientSession, url: str) -> Optional[dict]:
    if url in CACHE.evo:
        return CACHE.evo[url]
    data = await fetch_json(session, url)
    if data:
        CACHE.evo[url] = data
    return data

# -----------------------------------------------------------------------------
# Evolution helpers (context-aware modern method + no-duplicate render)
# -----------------------------------------------------------------------------

def _best_evo_detail(details: List[dict], target_slug: str, current_variant_slug: str) -> Optional[dict]:
    """
    Choose the most user-expected rule, taking into account:
      - target species slug (e.g., slowking),
      - the CURRENT VARIANT you queried (e.g., slowpoke-galar).
    Rules:
      • If current is Galarian, prefer Galarica Cuff/Wreath.
      • If current is NOT Galarian, avoid Galarica items; prefer King's Rock for Slowking.
      • Prefer modern item methods (Leaf/Ice Stone) over old location methods (Leafeon/Glaceon).
      • Trade+held item > trade > informative level-up > location-only.
    """
    if not details:
        return None

    cslug = (current_variant_slug or "").lower()

    def richness(d: dict) -> int:
        keys = [
            "trigger","min_level","item","held_item","min_happiness","min_affection","min_beauty",
            "time_of_day","known_move","known_move_type","location","needs_overworld_rain",
            "party_species","party_type","relative_physical_stats","trade_species","turn_upside_down"
        ]
        return sum(1 for k in keys if d.get(k))

    def score(d: dict) -> int:
        s = 0
        trig = (d.get("trigger") or {}).get("name", "")
        item_name = (d.get("item") or {}).get("name", "") if d.get("item") else ""
        held_name = (d.get("held_item") or {}).get("name", "") if d.get("held_item") else ""

        # Prefer modern item evolutions
        if trig == "use-item":
            s += 100
            if item_name in {"leaf-stone", "ice-stone"}:
                s += 15
            # Context-sensitive: Galarica only if current is Galarian
            if item_name in {"galarica-wreath", "galarica-cuff"}:
                s += 40 if "-galar" in cslug else -80

        # Trade hierarchy
        if trig == "trade":
            s += 60
            if held_name:
                s += 15  # e.g., King's Rock for classic Slowking
            if d.get("trade_species"):
                s += 5

        # Level-up preferences
        if trig == "level-up":
            s += 40
            if d.get("min_level"): s += 4
            if d.get("min_happiness") or d.get("min_affection"): s += 8
            if d.get("time_of_day"): s += 6
            if d.get("known_move"): s += 5
            if d.get("known_move_type"): s += 7
            if d.get("relative_physical_stats") is not None: s += 3
            if d.get("needs_overworld_rain"): s += 2
            if d.get("location"): s -= 30  # de-prioritize older location-only variants

        # Extra penalty for pure location-only edges
        if d.get("location") and not (d.get("item") or d.get("min_happiness") or d.get("known_move_type") or d.get("time_of_day")):
            s -= 40

        # Slight bonus for overall informativeness
        s += min(richness(d), 8)
        return s

    return sorted(details, key=lambda d: (score(d), richness(d)), reverse=True)[0]

def _nice_item(obj: Optional[dict]) -> Optional[str]:
    if not obj: return None
    return obj["name"].replace("-", " ").title()

def _nice_move_or_type(obj: Optional[dict]) -> Optional[str]:
    if not obj: return None
    return obj["name"].replace("-", " ").title()

def format_evo_condition(detail: Optional[dict]) -> str:
    if not detail: return ""
    trigger = (detail.get("trigger") or {}).get("name", "")
    trig = trigger.replace("-", " ")
    parts: List[str] = []

    item = _nice_item(detail.get("item"))
    held = _nice_item(detail.get("held_item"))
    trade_species = _nice_move_or_type(detail.get("trade_species"))
    kmove = _nice_move_or_type(detail.get("known_move"))
    kmtype = _nice_move_or_type(detail.get("known_move_type"))
    loc = _nice_item(detail.get("location"))
    tod = detail.get("time_of_day") or ""

    lvl = detail.get("min_level")
    happy = detail.get("min_happiness")
    beauty = detail.get("min_beauty")
    affection = detail.get("min_affection")
    rain = detail.get("needs_overworld_rain")
    upsidedown = detail.get("turn_upside_down")
    rel_stats = detail.get("relative_physical_stats")

    if trigger == "use-item" and item:
        parts.append(item)
    elif trigger == "trade":
        if held: parts.append(f"held {held} + trade")
        elif trade_species: parts.append(f"trade for {trade_species}")
        else: parts.append("trade")
    elif trigger == "level-up":
        if lvl: parts.append(f"lvl {lvl}")
        if happy: parts.append("friendship")
        if beauty: parts.append("beauty")
        if affection: parts.append("affection")
        if tod: parts.append(f"{tod}time")
        if kmove: parts.append(f"knows {kmove}")
        if kmtype: parts.append(f"knows {kmtype} move")
        if loc: parts.append(f"at {loc}")
        if rain: parts.append("overworld rain")
        if upsidedown: parts.append("hold console upside down")
        if rel_stats is not None:
            if   rel_stats > 0: parts.append("Atk > Def")
            elif rel_stats < 0: parts.append("Atk < Def")
            else:               parts.append("Atk = Def")

    else:
        if trig: parts.append(trig)

    return " + ".join(parts) if parts else trig

def _render_subtree(
        node: dict,
        bold_slug: str,
        context_variant_slug: str,
        prefix: str = "",
        is_last: bool = True,
        is_root: bool = True,
        print_self: bool = True,
) -> List[str]:
    """
    Render the evolution subtree:
      - bold_slug: species slug to bold (base species name)
      - context_variant_slug: the concrete variant being viewed (affects method selection)
    Avoids printing the same child twice by only printing descendants after the child line.
    """
    lines: List[str] = []

    # Optionally print this node (root prints without branch characters)
    if print_self:
        slug = node["species"]["name"]
        name = slug_to_display(slug)
        here = f"**{name}**" if slug == bold_slug else name
        if is_root:
            lines.append(here)
        else:
            branch = "└─ " if is_last else "├─ "
            lines.append(prefix + branch + here)

    children = node.get("evolves_to", []) or []
    for idx, child in enumerate(children):
        last = (idx == len(children) - 1)

        child_slug = child["species"]["name"]
        # Choose best detail WITH context of the exact variant the user queried
        detail = _best_evo_detail(child.get("evolution_details", []), child_slug, current_variant_slug=context_variant_slug)
        cond = format_evo_condition(detail)

        child_name = slug_to_display(child_slug)
        child_disp = f"**{child_name}**" if child_slug == bold_slug else child_name

        # Compute prefixes/branches for this level
        branch_prefix = prefix + ("" if is_root else ("   " if is_last else "│  "))
        branch = "└─ " if last else "├─ "

        # Print the child line once (with condition)
        head = branch_prefix + branch + child_disp
        if cond:
            head += f" ({cond})"
        lines.append(head)

        # Recurse only into descendants (avoid reprinting child)
        grand = child.get("evolves_to", [])
        if grand:
            deeper_prefix = branch_prefix + ("   " if last else "│  ")
            lines.extend(
                _render_subtree(
                    child,
                    bold_slug=bold_slug,
                    context_variant_slug=context_variant_slug,
                    prefix=deeper_prefix,
                    is_last=last,
                    is_root=False,
                    print_self=False,
                )
            )

    return lines

# -----------------------------------------------------------------------------
# Cog
# -----------------------------------------------------------------------------

class UpdatedDexter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dex", aliases=["pokedex"])
    async def dex(self, ctx: commands.Context, pkmn: str, *form_input: str):
        """
        Usage examples:
          .dex deoxys
          .dex deoxys attack
          .dex slowpoke galarian
          .dex meowth alolan
          .dex sneasel hisuian
          .dex tauros paldean fire
          .dex tauros paldean water
          .dex charizard gmax
          .dex charizard mega-x
          .dex charizard shiny
        """
        async with aiohttp.ClientSession() as session:
            base_key = normalize_key(pkmn)

            # Determine requested variant(s)
            mega_suf = requested_mega_suffix(form_input)
            form_suf = requested_form_suffix(form_input, base_key)

            # Try order: Mega first (if asked), then specific form, then base
            pj = None
            tried = set()

            if mega_suf:
                for suf in ([mega_suf] if mega_suf in {"-mega", "-mega-x", "-mega-y"} else []):
                    key = base_key + suf
                    tried.add(key)
                    pj = await get_pokemon(session, key)
                    if not pj and suf == "-mega":
                        # Fallback: some species only have X/Y
                        for alt in ("-mega-x", "-mega-y"):
                            key2 = base_key + alt
                            tried.add(key2)
                            pj = await get_pokemon(session, key2)
                            if pj: break
                    if pj: break

            if not pj and form_suf:
                key = base_key + form_suf
                tried.add(key)
                pj = await get_pokemon(session, key)

            if not pj:
                tried.add(base_key)
                pj = await get_pokemon(session, base_key)

            if not pj and pkmn not in tried:
                pj = await get_pokemon(session, pkmn)

            if not pj:
                await ctx.send("I couldn't find that Pokémon on PokeAPI.")
                return

            # species via URL (works for forms/megas/base)
            species_url = (pj.get("species") or {}).get("url")
            species = await get_species_by_url(session, species_url) if species_url else None
            if not species:
                await ctx.send("I found the Pokémon, but couldn't load its species data.")
                return

            # Dex number uses base species id (so Megas/Forms still show base #)
            dex_number = species["id"]

            # current_slug is the concrete variant (e.g., slowpoke-galar, deoxys-attack)
            current_slug = pj["name"]

            # display name: use Mega title if applicable; otherwise species display
            base_display = slug_to_display(species["name"])
            if current_slug.endswith(("-mega", "-mega-x", "-mega-y")):
                display_name = nice_mega_title(base_display, current_slug)
            else:
                display_name = base_display

            # Derived fields from the selected entry (variant-aware)
            t1, t2 = types_display(pj["types"])
            abilities = abilities_to_named(pj["abilities"])

            base_stats = {s["stat"]["name"]: s["base_stat"] for s in pj["stats"]}
            stat_block = {
                "hp": base_stats.get("hp"),
                "atk": base_stats.get("attack"),
                "def": base_stats.get("defense"),
                "spA": base_stats.get("special-attack"),
                "spD": base_stats.get("special-defense"),
                "spe": base_stats.get("speed"),
            }
            stat_block["tot"] = sum(v for v in stat_block.values() if isinstance(v, int))

            # Species extras
            capture_rate = species.get("capture_rate", None)
            egg_groups = [_title(e["name"]) for e in species.get("egg_groups", [])]

            # Megas from species varieties
            varieties = species.get("varieties", [])
            mega_tokens: List[str] = []
            form_labels: List[str] = []
            for v in varieties:
                vname: str = v["pokemon"]["name"]
                token = mega_display_tokens(vname)
                if token and token not in mega_tokens:
                    mega_tokens.append(token)
                else:
                    label = form_label_from_variety(vname)
                    if label and label not in form_labels:
                        form_labels.append(label)

            has_mega = len(mega_tokens) > 0
            mega_tokens.sort(key=lambda s: {"Mega": 0, "Mega X": 1, "Mega Y": 2}.get(s, 99))
            forms_line = ""
            if form_labels:
                forms_line = "Forms: `" + ", ".join(form_labels) + "`"

            # Evolution tree (bold base species; choose methods with current variant context)
            evo_line = ""
            evo_url = (species.get("evolution_chain") or {}).get("url")
            if evo_url:
                evo_data = await get_evolution_chain(session, evo_url)
                if evo_data and evo_data.get("chain"):
                    tree_lines = _render_subtree(
                        evo_data["chain"],
                        bold_slug=species["name"],
                        context_variant_slug=current_slug,
                        is_root=True,
                    )
                    evo_line = "\n" + "\n".join(tree_lines) + "\n"

            # Sprite (variant-aware) + shiny
            shiny = is_shiny_requested(form_input)
            sprite = sprite_url(current_slug, shiny)

            # Build embed
            embed = discord.Embed(
                title=f"__#{dex_number} {display_name}__",
                colour=0xFF0000
            )

            # Misc. Info
            type_txt = f"Type: `{t1}`" + ("" if not t2 else f"/`{t2}`")
            egg_txt = ", ".join(egg_groups) if egg_groups else "Unknown"
            misc_lines = [
                type_txt,
                f"Catch rate: `{capture_rate}`" if capture_rate is not None else "Catch rate: `?`",
                f"Egg Groups: `{egg_txt}`",
            ]
            if forms_line:
                misc_lines.append(forms_line)

            # Has Mega
            if has_mega:
                if mega_tokens:
                    misc_lines.append(f"Has Mega: `True ({', '.join(mega_tokens)})`")
                else:
                    misc_lines.append("Has Mega: `True`")
            else:
                misc_lines.append("Has Mega: `False`")

            # Abilities
            ability_list = [abilities[k] for k in ("ability1", "ability2", "abilityH") if abilities.get(k)]
            if ability_list:
                if len(ability_list) == 3:
                    ability_text = f"Ability 1: `{ability_list[0]}`\nAbility 2: `{ability_list[1]}`\nAbility H: `{ability_list[2]}`"
                elif len(ability_list) == 2:
                    if abilities.get("ability1") and abilities.get("abilityH"):
                        ability_text = f"Ability 1: `{abilities['ability1']}`\nAbility H: `{abilities['abilityH']}`"
                    else:
                        ability_text = f"Ability 1: `{ability_list[0]}`\nAbility 2: `{ability_list[1]}`"
                else:
                    ability_text = f"Ability 1: `{ability_list[0]}`"
            else:
                ability_text = "—"

            # Base stats
            stats_text = (
                "__`HP     Atk     Def`__\n"
                f"__`{str(stat_block['hp']):<7}{str(stat_block['atk']):<8}{str(stat_block['def']):<3}`__\n"
                "__`SpA    SpD     Spe`__\n"
                f"__`{str(stat_block['spA']):<7}{str(stat_block['spD']):<8}{str(stat_block['spe']):<3}`__\n"
                f"__`Total: {stat_block['tot']}`__"
            )

            # Image + Evolution tree
            embed.add_field(name="Misc. Info", value="\n".join(misc_lines))
            embed.add_field(name="Abilities", value=ability_text, inline=True)
            embed.add_field(name="Base stats:", value=stats_text)
            embed.set_image(url=sprite)
            if evo_line:
                embed.add_field(name="Evolution", value=evo_line, inline=False)

            await ctx.send(embed=embed)


# Setup function for your bot
async def setup(bot: commands.Bot):
    await bot.add_cog(UpdatedDexter(bot))
