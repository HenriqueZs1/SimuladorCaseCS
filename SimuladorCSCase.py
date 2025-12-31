import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
import random

try:
    from data.LOW_CASE import LOW_CASE
    from data.AMBER_CASE import AMBER_CASE
    from data.USP_CASE import USP_CASE
    from data.AK_CASE import AK_CASE
    from data.ULTRA_CASE import ULTRA_CASE
    from data.DISC_CASE import DISC_CASE
    from data.MEDIUM_CASE import MEDIUM_CASE
    from data.ELEGANT_CASE import ELEGANT_CASE
    from data.HYPER_CASE import HYPER_CASE
    from data.WINTER_CASE import WINTER_CASE    
except ImportError as e:
    print(f"ERRO CRÍTICO DE IMPORTAÇÃO: Não foi possível carregar módulos de dados. Verifique a pasta 'data'. Erro: {e}")
    messagebox.showerror("Erro de Arquivo", "Não foi possível encontrar ou importar a pasta 'data'. O simulador será encerrado.")
    exit()
    
# ======================
# MODELOS (CLASSES)
# ======================
class Player:
    def __init__(self, initial_balance):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.inventory = []
        self.total_spent = 0

    def can_open_case(self, price):
        return self.balance >= price

    def remove_balance(self, value):
        self.balance -= value
        self.total_spent += value

    def add_skin(self, skin):
        self.inventory.append(skin)
        
    def calculate_profit(self):
        inventory_value = sum(item.get('price', 0) for item in self.inventory)
        profit = (self.balance + inventory_value) - self.initial_balance
        return profit


class Case:
    def __init__(self, name, price, skins):
        self.name = name
        self.price = price
        self.skins = skins

    def open(self, player):
        if not player.can_open_case(self.price):
            # Apenas retorna None sem erro, não mostrar mensagem
            return None, None  

        player.remove_balance(self.price)
        skin = weighted_random(self.skins)
        player.add_skin(skin)
        return skin, None

# ======================
# UTIL
# ======================
def weighted_random(skins):
    valid_skins = [skin for skin in skins if isinstance(skin.get("odds"), (int, float))]
    if not valid_skins:
        if skins:
            return random.choice(skins) 
        return {"weapon": "N/A", "skin": "ERROR", "wear": "N/A", "price": 0.0, "odds": 0.0}
    odds = [skin["odds"] for skin in valid_skins]
    return random.choices(valid_skins, weights=odds, k=1)[0]

# ======================
# INICIALIZAÇÃO DE OBJETOS
# ======================
DEFAULT_INITIAL_BALANCE = 200 

cases_data_map = {
    "Low Case": LOW_CASE,
    "Amber Case": AMBER_CASE,
    "Usp Case": USP_CASE,
    "Ak_case": AK_CASE,
    "Ultra Case": ULTRA_CASE,
    "Disc Case": DISC_CASE,
    "Medium Case": MEDIUM_CASE,
    "Elegant Case": ELEGANT_CASE,
    "Hyper Case": HYPER_CASE,
    "Winter Case": WINTER_CASE
}

cases = {
    key: Case(data["name"], data["price"], data["skins"])
    for key, data in cases_data_map.items()
}
player = None 

# ======================
# INTERFACE E LÓGICA
# ======================
root = tk.Tk()
root.title("CS Case Simulator")
root.geometry("920x800") 
root.resizable(False, False)

# --- Configuração de Estilos (ttk) ---
style = ttk.Style(root)
style.theme_use('clam') 

# Cores
COLOR_BG = "#2C2F33"        
COLOR_PRIMARY = "#5865F2"   
COLOR_SECONDARY = "#4F545C" 
COLOR_TEXT_LIGHT = "#FFFFFF" 
COLOR_ACCENT_PROFIT = "#38C238" 
COLOR_WARNING_LOSS = "#F04747"  
COLOR_DROP_LEGENDARY = "#FFD700" 
COLOR_DROP_MYTHICAL = "#800080"  
COLOR_DROP_RARE = "#00BFFF"      
COLOR_TEXT_INVENTORY = "#23272A" 

root.configure(bg=COLOR_BG)
GLOBAL_FONT = ("Arial", 11) 

# Estilos de Labels
style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_LIGHT, font=GLOBAL_FONT)
style.configure("Title.TLabel", font=("Arial", 22, "bold"), foreground=COLOR_TEXT_LIGHT)
style.configure("Result.TLabel", font=("Arial", 12))
style.configure("Profit.TLabel", font=("Arial", 14, "bold")) 
style.configure("Control.TFrame", background=COLOR_SECONDARY) 

# Estilos de Botões
style.configure("Action.TButton", 
    font=("Arial", 12, "bold"), 
    padding=(15, 10), 
    foreground=COLOR_TEXT_LIGHT, 
    background=COLOR_PRIMARY, 
    relief="flat"
)
style.map("Action.TButton", background=[('active', COLOR_PRIMARY), ('pressed', COLOR_PRIMARY)])

style.configure("Reset.TButton", 
    font=("Arial", 11, "bold"), 
    padding=(10, 8), 
    foreground=COLOR_TEXT_LIGHT, 
    background=COLOR_WARNING_LOSS, 
    relief="flat"
)
style.map("Reset.TButton", background=[('active', COLOR_WARNING_LOSS), ('pressed', COLOR_WARNING_LOSS)])

# Input de Saldo
style.configure("Balance.TEntry", 
    fieldbackground=COLOR_TEXT_INVENTORY, 
    foreground=COLOR_DROP_LEGENDARY, 
    borderwidth=1, 
    relief="flat", 
    font=("Consolas", 11, "bold")
)

# Variáveis
saldo_var = tk.StringVar()
resultado_var = tk.StringVar()
lucro_var = tk.StringVar() 
case_var = tk.StringVar(value=next(iter(cases.keys()), "Nenhuma Caixa"))
case_price_var = tk.StringVar()
initial_balance_input_var = tk.StringVar(value=str(DEFAULT_INITIAL_BALANCE)) 

def update_case_price(*args):
    case_name = case_var.get()
    if case_name in cases:
        price = cases[case_name].price
        case_price_var.set(f"R$ {price:.2f}") 
    else:
        case_price_var.set("N/A")

case_var.trace_add("write", update_case_price)

def atualizar_tela():
    if not player:
        saldo_var.set("💰 Saldo Atual: R$N/A | 💸 Total Gasto: R$N/A")
        lucro_var.set("❌ Prejuízo: R$N/A")
        inventario_box.delete("1.0", tk.END)
        update_case_price()
        return

    profit = player.calculate_profit()
    saldo_var.set(f"💰 Saldo Atual: R${player.balance:.2f} | 💸 Total Gasto: R${player.total_spent:.2f}")
    
    if profit >= 0:
        lucro_label.config(foreground=COLOR_ACCENT_PROFIT)
        lucro_var.set(f"✅ Lucro: R${profit:.2f}")
    else:
        lucro_label.config(foreground=COLOR_WARNING_LOSS)
        lucro_var.set(f"❌ Prejuízo: R${abs(profit):.2f}") 
    
    update_case_price() 
    inventario_box.delete("1.0", tk.END)
    sorted_inventory = sorted(player.inventory, key=lambda x: x.get('price', 0), reverse=True)
    
    for item in sorted_inventory:
        price = item.get('price', 0)
        odds_value = item.get('odds', None)
        odds_display = f" | Chance: {odds_value:.3f}%" if odds_value is not None else ""
        
        if price > 100: cor_raridade = COLOR_DROP_LEGENDARY
        elif price > 50: cor_raridade = COLOR_DROP_MYTHICAL
        elif price > 10: cor_raridade = COLOR_DROP_RARE
        else: cor_raridade = "white"

        line = (
            f"R${price:<8.2f} | {item.get('weapon', 'N/A'):<10} | "
            f"{item.get('skin', 'N/A'):<30} ({item.get('wear', 'N/A')})"
            f"{odds_display}\n" 
        )
        inventario_box.insert(tk.END, line)
        start_index = inventario_box.search(line.strip(), "1.0", stopindex=tk.END, regexp=False)
        if start_index:
            end_index = f"{start_index.split('.')[0]}.end"
            tag_name = f"color_{id(item)}"
            inventario_box.tag_config(tag_name, foreground=cor_raridade)
            inventario_box.tag_add(tag_name, start_index, end_index)

def abrir_caixa():
    if player is None:
        return
    case_name = case_var.get()
    if case_name not in cases:
        return
        
    case_selecionada = cases[case_name]
    skin, _ = case_selecionada.open(player)
    
    if skin is None:
        return

    price = skin.get('price', 0)
    if price > 100: cor_drop = COLOR_DROP_LEGENDARY
    elif price > 50: cor_drop = COLOR_DROP_MYTHICAL
    elif price > 10: cor_drop = COLOR_DROP_RARE
    else: cor_drop = COLOR_ACCENT_PROFIT
        
    resultado_label.config(foreground=cor_drop)
    resultado_var.set(
        f"🎉 DROP: {skin.get('weapon', 'N/A')} | {skin.get('skin', 'N/A')} "
        f"({skin.get('wear', 'N/A')}) - R${price:.2f}"
    )
    atualizar_tela()

def abrir_tres_caixas():
    if player is None:
        return
    case_name = case_var.get()
    if case_name not in cases:
        return
        
    case_selecionada = cases[case_name]
    drops = []
    total_gasto_multi = 0

    for _ in range(3):
        skin, _ = case_selecionada.open(player)
        if skin is None:
            break
        drops.append(f"R${skin.get('price', 0):.2f} | {skin.get('weapon', 'N/A')} - {skin.get('skin', 'N/A')} ({skin.get('wear', 'N/A')})")
        total_gasto_multi += case_selecionada.price

    if drops:
        resultado_label.config(foreground=COLOR_ACCENT_PROFIT)
        resultado_var.set(f"Drops (3x - Total Gasto: R${total_gasto_multi:.2f}):\n" + "\n".join(drops))
    
    atualizar_tela()

def reset_game():
    global player
    try:
        new_initial_balance = float(initial_balance_input_var.get().replace(",", "."))
        if new_initial_balance < 0:
             raise ValueError("Saldo deve ser positivo.")
    except ValueError:
        new_initial_balance = DEFAULT_INITIAL_BALANCE
        initial_balance_input_var.set(str(DEFAULT_INITIAL_BALANCE)) 

    player = Player(initial_balance=new_initial_balance) 
    resultado_var.set("Jogo Reiniciado. Escolha uma caixa para começar!")
    atualizar_tela()

def mostrar_top_skins():
    if player is None or not player.inventory:
        return
    sorted_inventory = sorted(player.inventory, key=lambda x: x.get('price', 0), reverse=True)
    top_3 = sorted_inventory[:3]
    display_text = "💎 Top 3 Skins Mais Caras:\n\n"
    for i, item in enumerate(top_3):
        display_text += (
            f"#{i+1}: R${item.get('price', 0):.2f} | {item.get('weapon', 'N/A')} - {item.get('skin', 'N/A')} "
            f"({item.get('wear', 'N/A')})\n"
        )
    messagebox.showinfo("Top Skins", display_text)

# ======================
# WIDGETS
# ======================
ttk.Label(root, text="🎁 CS Case Simulator", style="Title.TLabel").pack(pady=20)

control_main_frame = ttk.Frame(root, style="Control.TFrame")
control_main_frame.pack(pady=10, padx=20)
ttk.Label(control_main_frame, text="Saldo Inicial (R$):", font=GLOBAL_FONT, background=COLOR_SECONDARY).grid(row=0, column=0, padx=10, pady=10, sticky='w')

initial_balance_entry = ttk.Entry(
    control_main_frame, 
    textvariable=initial_balance_input_var, 
    width=10, 
    justify='center', 
    style="Balance.TEntry"
)
initial_balance_entry.grid(row=0, column=1, padx=5, pady=10, sticky='w')

ttk.Button(control_main_frame, text="🔁 REINICIAR JOGO", command=reset_game, style="Reset.TButton").grid(row=0, column=2, padx=(20, 10), pady=10, sticky='e')

saldo_label = ttk.Label(root, textvariable=saldo_var, font=("Arial", 12))
saldo_label.pack(pady=5)
lucro_label = ttk.Label(root, textvariable=lucro_var, style="Profit.TLabel")
lucro_label.pack(pady=5)

case_select_frame = ttk.Frame(root, style="Control.TFrame")
case_select_frame.pack(pady=10)
ttk.Label(case_select_frame, text="📦 Caixa Selecionada:", font=("Arial", 12, "bold"), background=COLOR_BG).grid(row=0, column=0, padx=10, pady=10)

case_menu = tk.OptionMenu(case_select_frame, case_var, *cases.keys())
case_menu.config(bg=COLOR_PRIMARY, fg=COLOR_TEXT_LIGHT, activebackground=COLOR_PRIMARY, 
    activeforeground=COLOR_TEXT_LIGHT, font=GLOBAL_FONT, relief=tk.FLAT)
case_menu["menu"].config(bg=COLOR_TEXT_INVENTORY, fg=COLOR_TEXT_LIGHT)
case_menu.grid(row=0, column=1, padx=10, pady=10)

price_label = ttk.Label(case_select_frame, textvariable=case_price_var, font=("Arial", 14, "bold"), foreground=COLOR_DROP_LEGENDARY, background=COLOR_BG)
price_label.grid(row=0, column=2, padx=20, pady=10) 

button_frame = ttk.Frame(root, style="Control.TFrame")
button_frame.pack(pady=15)

ttk.Button(button_frame, text="💥 Abrir 1 Caixa", command=abrir_caixa, style="Action.TButton").pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="🔥 Abrir 3 Caixas", command=abrir_tres_caixas, style="Action.TButton").pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="🌟 Ver Top 3 Skins", command=mostrar_top_skins, style="Action.TButton").pack(side=tk.LEFT, padx=10)

resultado_label = ttk.Label(root, textvariable=resultado_var, style="Result.TLabel")
resultado_label.pack(pady=15)

ttk.Label(root, text="Inventário (Ordenado por Preço):", font=("Arial", 14, "bold")).pack(pady=(10, 5))

inventory_frame = ttk.Frame(root, padding=5, relief=tk.RIDGE, borderwidth=1, style="Control.TFrame")
inventory_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(inventory_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

inventario_box = tk.Text(
    inventory_frame, height=15, width=75,
    bg=COLOR_TEXT_INVENTORY, fg=COLOR_TEXT_LIGHT,
    font=("Consolas", 11), yscrollcommand=scrollbar.set,
    borderwidth=0, relief="flat", insertbackground=COLOR_TEXT_LIGHT 
)
inventario_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=inventario_box.yview)

# Inicialização
reset_game()
root.mainloop()
