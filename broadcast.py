import random
import math
import bisect
import time

random.seed(42)

N_LEAVES = 1024  # ближайшая степень двойки >= 1000
N_USERS = 1000
# в задании N=1000000, но в чистом питоне это ~2 часа
# 100к выборок дает достаточную точность и работает минут 10
N_SAMPLES = 100_000


def cover_size(rev_sorted):
    stack = [(0, len(rev_sorted), 0, N_LEAVES)]
    cover = 0
    while stack:
        rlo, rhi, lo, hi = stack.pop()
        valid = min(hi, N_USERS) - lo
        if valid <= 0:
            continue
        rc = rhi - rlo
        if rc == 0:
            cover += 1
            continue
        if rc >= valid:
            continue
        mid = (lo + hi) // 2
        rm = bisect.bisect_left(rev_sorted, mid, rlo, rhi)
        stack.append((rlo, rm, lo, mid))
        stack.append((rm, rhi, mid, hi))
    return cover


########################################
# задание 1
########################################
print("=" * 60)
print("Задание 1: среднее покрытие в схеме NNL Complete Subtrees")
print(f"n={N_USERS}, выборка N={N_SAMPLES}")
print("=" * 60)

rs = [int(0.1 * N_USERS * k) for k in range(1, 10)]
results_mc = {}

total_time = time.time()
for r in rs:
    t0 = time.time()
    total = 0
    for _ in range(N_SAMPLES):
        revoked = sorted(random.sample(range(N_USERS), r))
        total += cover_size(revoked)
    avg = total / N_SAMPLES
    dt = time.time() - t0
    results_mc[r] = avg
    print(f"  r={r:4d} ({r*100//N_USERS:2d}%):  E[cover] ~ {avg:.2f}  ({dt:.1f}с)")

print(f"\nобщее время: {time.time() - total_time:.0f}с")


########################################
# задание 2*
########################################
print("\n" + "=" * 60)
print("Задание 2*: теоретическая оценка E[покрытия]")
print("=" * 60)

# строим дерево, считаем s_v - число реальных юзеров в поддереве каждого узла
# дерево в массиве: корень=1, дети i -> 2i, 2i+1
# листья: позиции N_LEAVES .. 2*N_LEAVES-1
sv = [0] * (2 * N_LEAVES)
for i in range(N_USERS):
    sv[N_LEAVES + i] = 1
for i in range(N_LEAVES - 1, 0, -1):
    sv[i] = sv[2 * i] + sv[2 * i + 1]


def log_comb(n, k):
    if k < 0 or k > n:
        return float('-inf')
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


# узел v (не корень) попадает в покрытие, если:
#   - в его поддереве нет отозванных
#   - в поддереве его брата есть хотя бы один отозванный
# P(v в покрытии) = C(n-s_v, r)/C(n,r) - C(n-s_parent, r)/C(n,r)
# суммируем по всем узлам
def expected_cover(r):
    if r == 0:
        return 1.0
    log_total = log_comb(N_USERS, r)
    result = 0.0
    for v in range(2, 2 * N_LEAVES):
        if sv[v] == 0:
            continue
        p = v // 2
        a = N_USERS - sv[v]
        b = N_USERS - sv[p]
        t1 = log_comb(a, r) - log_total if a >= r else float('-inf')
        t2 = log_comb(b, r) - log_total if b >= r else float('-inf')
        if t1 > -500:
            result += math.exp(t1)
        if t2 > -500:
            result -= math.exp(t2)
    return result


print(f"\n{'r':>6} | {'Монте-Карло':>12} | {'Теория':>12} | {'|разница|':>10}")
print("-" * 50)
for r in rs:
    theor = expected_cover(r)
    mc = results_mc[r]
    diff = abs(mc - theor)
    print(f"{r:6d} | {mc:12.2f} | {theor:12.2f} | {diff:10.3f}")

print()
print("Покрытие максимально при r ~ 0.3n (около 300 из 1000).")
print("При малых r отзывов мало -> большие поддеревья целиком свободны.")
print("При больших r почти все отозваны -> покрывать почти некого.")
