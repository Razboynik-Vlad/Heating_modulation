import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('QtAgg')
import matplotlib.animation as animation

# ==========================================
# 1. КОНЦЕПЦИЯ HEATRAPY: ФИЗИЧЕСКИЕ СВОЙСТВА
# ==========================================
class MaterialPCM:
    def __init__(self):
        self.rho = 917.0        # Плотность (кг/м^3)
        self.cp = 2090.0        # Удельная теплоемкость (Дж/(кг*К))
        self.k_solid = 2.22     # Теплопроводность льда (Вт/(м*К))
        self.k_liquid = 0.58    # Теплопроводность воды (Вт/(м*К))
        self.L = 334000.0       # Латентная теплота плавления (Дж/кг)
        self.Tm = 0.0           # Температура плавления (Цельсий)
        self.dT = 0.5           # Полуширина зоны размытия плавления (К)

# ==========================================
# НАСТРОЙКА ЭКСПЕРИМЕНТА И ГЕОМЕТРИИ
# ==========================================
# Размеры расчетной области (в метрах)
LX, LY = 0.1, 0.1  
NX, NY = 60, 60  # Сетка
dx, dy = LX / NX, LY / NY

# Настройка положения объекта и источника тепла
# Вы можете менять эти координаты для изменения расстояния!
OBJECT_CENTER = (0.06, 0.05)  # Центр ледяного куба (x, y)
OBJECT_SIZE = 0.03            # Размер стороны куба
SOURCE_POS = (0.02, 0.01)     # Координаты точечного источника тепла
SOURCE_POWER = 8e7            # Мощность источника (Вт/м^3)
SOURCE_SIGMA = 0.004          # Радиус рассеивания тепла источника (м)

# Инициализация материала
mat = MaterialPCM()

# Определение критических точек энтальпии для пересчета температур
H_solid_max = mat.cp * (mat.Tm - mat.dT)
H_liquid_min = mat.cp * (mat.Tm + mat.dT) + mat.L

# ==========================================
# 2. МАТЕМАТИКА PHASE-CHANGE: ФУНКЦИИ СВЯЗИ
# ==========================================
def T_from_H(H_field):
    """ Векторизованный пересчет энтальпии в температуру """
    T_field = np.zeros_like(H_field)
    
    # Твердая фаза
    mask_solid = H_field < H_solid_max
    T_field[mask_solid] = H_field[mask_solid] / mat.cp
    
    # Жидкая фаза
    mask_liquid = H_field > H_liquid_min
    T_field[mask_liquid] = (H_field[mask_liquid] - mat.L) / mat.cp
    
    # Переходная зона (Mushy Zone)
    mask_mush = ~(mask_solid | mask_liquid)
    denom = mat.cp + mat.L / (2.0 * mat.dT)
    num = H_field[mask_mush] + mat.L * (mat.Tm - mat.dT) / (2.0 * mat.dT)
    T_field[mask_mush] = num / denom
    
    return T_field

def get_liquid_fraction(T_field):
    """ Определение доли жидкой фазы в каждой ячейке """
    fl = (T_field - (mat.Tm - mat.dT)) / (2.0 * mat.dT)
    return np.clip(fl, 0.0, 1.0)

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ПОЛЕЙ И СЕТКИ
# ==========================================
x = np.linspace(0, LX, NX)
y = np.linspace(0, LY, NY)
X, Y = np.meshgrid(x, y, indexing='ij')

# Построение матрицы температур: фон (вода, +2°C), объект (лед, -5°C)
T = np.ones((NX, NY)) * 2.0  

# Вырезаем геометрию объекта
ice_mask = (np.abs(X - OBJECT_CENTER[0]) <= OBJECT_SIZE / 2) & \
           (np.abs(Y - OBJECT_CENTER[1]) <= OBJECT_SIZE / 2)
T[ice_mask] = -5.0

# Переводим начальную температуру в энтальпию
fl_init = get_liquid_fraction(T)
H = mat.cp * T + mat.L * fl_init

# Формируем гауссов точечный источник тепла
Q = SOURCE_POWER * np.exp(-((X - SOURCE_POS[0])**2 + (Y - SOURCE_POS[1])**2) / (2.0 * SOURCE_SIGMA**2))

# Шаг по времени из критерия устойчивости Куранта
dt = 0.02  
steps_per_frame = 45  # Ускорение отрисовки

# Считаем начальную массу льда для графика (%)
initial_ice_mass = np.sum((1.0 - fl_init)[ice_mask]) * mat.rho * dx * dy

# Списки истории для правого графика (используем list() вместо пустых скобок)
time_history = list()
mass_history = list()

# ==========================================
# 3. АРХИТЕКТУРА: ВЕКТОРИЗАЦИЯ И ДАШБОРД
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("2D Симулятор плавления вещества с подвижным источником", fontsize=14)

# Левый график: Температурное поле
im = ax1.imshow(T.T, extent=[0, LX, 0, LY], origin='lower', cmap='coolwarm', vmin=-6, vmax=15)
source_marker, = ax1.plot(SOURCE_POS[0], SOURCE_POS[1], 'ro', markersize=8, label='Источник тепла')
ax1.set_xlabel("X (метры)")
ax1.set_ylabel("Y (метры)")
ax1.set_title("Тепловое поле и фронт плавления")
ax1.legend(loc='upper left')
cb = fig.colorbar(im, ax=ax1, label="Температура (°C)")

# Правый график: Масса объекта от времени
mass_line, = ax2.plot(np.array(list()), np.array(list()), 'b-', lw=2)
ax2.set_xlim(0, 45)
ax2.set_ylim(0, 105)
ax2.set_xlabel("Время (секунды)")
ax2.set_ylabel("Оставшаяся масса льда (%)")
ax2.set_title("Зависимость массы объекта от времени")
ax2.grid(True)

# Переменная для хранения контура изотермы фронта
contour_holder = None

def update(frame):
    global H, contour_holder
    
    # Просчитываем физику внутри кадра векторизованно
    for _ in range(steps_per_frame):
        T_current = T_from_H(H)
        fl_current = get_liquid_fraction(T_current)
        
        # Эффективная теплопроводность на границах фаз
        k = mat.k_solid + (mat.k_liquid - mat.k_solid) * fl_current
        
        # Векторизованный расчет потоков через NumPy-срезы
        flux_x_R = 0.5 * (k[1:-1, 1:-1] + k[2:, 1:-1]) * (T_current[2:, 1:-1] - T_current[1:-1, 1:-1]) / dx**2
        flux_x_L = 0.5 * (k[1:-1, 1:-1] + k[:-2, 1:-1]) * (T_current[1:-1, 1:-1] - T_current[:-2, 1:-1]) / dx**2
        flux_y_U = 0.5 * (k[1:-1, 1:-1] + k[1:-1, 2:]) * (T_current[1:-1, 2:] - T_current[1:-1, 1:-1]) / dy**2
        flux_y_D = 0.5 * (k[1:-1, 1:-1] + k[1:-1, :-2]) * (T_current[1:-1, 1:-1] - T_current[1:-1, :-2]) / dy**2
        
        # Обновление внутренних ячеек энтальпии
        H[1:-1, 1:-1] += (dt / mat.rho) * (flux_x_R - flux_x_L + flux_y_U - flux_y_D + Q[1:-1, 1:-1])
        
        # Граничные условия (теплоизоляция краев)
        H[0, :] = H[1, :]
        H[-1, :] = H[-2, :]
        H[:, 0] = H[:, 1]
        H[:, -1] = H[:, -2]

    # Актуализируем финальные физические поля для текущего кадра
    T_final = T_from_H(H)
    fl_final = get_liquid_fraction(T_final)
    
    # Текущее время
    current_time = frame * dt * steps_per_frame
    
    # Расчет текущей массы льда строго внутри исходных границ объекта
    current_ice_mass = np.sum((1.0 - fl_final)[ice_mask]) * mat.rho * dx * dy
    mass_percentage = (current_ice_mass / initial_ice_mass) * 100.0 if initial_ice_mass > 0 else 0
    
    # Запись истории данных
    time_history.append(current_time)
    mass_history.append(mass_percentage)
    
    # Обновление графики теплового поля
    im.set_array(T_final.T)
    
    if contour_holder is not None:
        contour_holder.remove()
        contour_holder = None
    
    # Отрисовка четкой изолинии фронта плавления (T = 0°C)
    if np.min(T_final) < mat.Tm < np.max(T_final):
        contour_holder = ax1.contour(X, Y, T_final, levels=[mat.Tm], colors='white', linewidths=1.5)
        
    # Обновление графика массы
    mass_line.set_data(np.array(time_history), np.array(mass_history))
    
    # Динамическое масштабирование оси времени
    if current_time > ax2.get_xlim()[1]:
        ax2.set_xlim(0, current_time * 1.3)
        
    return im, mass_line

# Запуск интерактивной анимации
ani = animation.FuncAnimation(fig, update, frames=120, interval=40, blit=False)
plt.tight_layout()
plt.show()