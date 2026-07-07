import streamlit as st
import pandas as pd
import numpy as np


# =========================
# Core KCI calculation
# =========================

def normalize_score(x: float) -> float:
    """
    Convert 1-5 score to 0-1 scale.
    Formula: normalized = (score - 1) / 4
    """
    return (x - 1.0) / 4.0


def calculate_vertical_maturity(K: float, A: float, U: float, C: float, tau: float = 3.0):
    """
    Calculate vertical maturity based on sequential KAUC achievement.
    The rule uses raw 1-5 layer scores and threshold tau.
    """
    if K < tau:
        m = 0
        bottleneck = "Knowledge bottleneck"
        interpretation = "Nền tảng nhận thức/giá trị chưa đạt ngưỡng."
    elif A < tau:
        m = 1
        bottleneck = "Action bottleneck"
        interpretation = "Có nhận thức nhưng chưa chuyển hóa thành hành động."
    elif U < tau:
        m = 2
        bottleneck = "Utility bottleneck"
        interpretation = "Có hành động nhưng chưa tạo hoặc cảm nhận đủ lợi ích."
    elif C < tau:
        m = 3
        bottleneck = "Contribution bottleneck"
        interpretation = "Có sử dụng/hưởng lợi nhưng chưa đóng góp lại cho hệ thống."
    else:
        m = 4
        bottleneck = "Full KAUC profile"
        interpretation = "Các lớp K-A-U-C đều đạt ngưỡng theo trình tự."

    VM = m / 4.0
    return m, VM, bottleneck, interpretation


def calculate_kci(K: float, A: float, U: float, C: float, tau: float = 3.0):
    """
    Calculate KAUC Cultural Index.
    Inputs K, A, U, C must be on 1-5 scale.
    """

    # Normalize to 0-1
    k = normalize_score(K)
    a = normalize_score(A)
    u = normalize_score(U)
    c = normalize_score(C)

    # Horizontal intensity
    HI_equal = (k + a + u + c) / 4.0
    HI_weighted = (1 * k + 2 * a + 3 * u + 4 * c) / 10.0

    # Vertical maturity
    m, VM, bottleneck, interpretation = calculate_vertical_maturity(K, A, U, C, tau)

    # Final KCI
    KCI_weighted = 100.0 * HI_weighted * VM
    KCI_equal = 100.0 * HI_equal * VM

    # Simple normalized average for comparison
    simple_normalized_average = HI_equal

    return {
        "K": K,
        "A": A,
        "U": U,
        "C": C,
        "k": k,
        "a": a,
        "u": u,
        "c": c,
        "HI_equal": HI_equal,
        "HI_weighted": HI_weighted,
        "m": m,
        "VM": VM,
        "KCI_weighted": KCI_weighted,
        "KCI_equal": KCI_equal,
        "simple_normalized_average": simple_normalized_average,
        "bottleneck": bottleneck,
        "interpretation": interpretation
    }


def mean_layer_score(values):
    """
    Calculate mean score for one KAUC layer.
    """
    values = np.array(values, dtype=float)
    return float(np.mean(values))


# =========================
# Streamlit Interface
# =========================

st.set_page_config(
    page_title="KAUC Cultural Index Calculator",
    page_icon="📊",
    layout="wide"
)

st.title("KAUC Cultural Index Calculator")
st.caption("Interface nhập điểm bảng hỏi và tính KAUC Hybrid Cultural Index – KCI")

st.markdown(
    """
    App này tính chỉ số **KCI** theo 4 lớp:

    - **K – Knowledge**
    - **A – Action**
    - **U – Utility**
    - **C – Contribution**

    Công thức chính:

    \\[
    KCI = 100 \\times HI^W \\times VM
    \\]

    trong đó:

    \\[
    HI^W = \\frac{1k + 2a + 3u + 4c}{10}
    \\]

    và:

    \\[
    k = \\frac{K-1}{4}, \\quad
    a = \\frac{A-1}{4}, \\quad
    u = \\frac{U-1}{4}, \\quad
    c = \\frac{C-1}{4}
    \\]
    """
)

st.divider()

# Sidebar configuration
st.sidebar.header("Cấu hình tính toán")

tau = st.sidebar.slider(
    "Ngưỡng trưởng thành τ",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.1,
    help="Ngưỡng mặc định trong bài là τ = 3 trên thang 1–5."
)

input_mode = st.sidebar.radio(
    "Kiểu nhập dữ liệu",
    [
        "Nhập điểm lớp K/A/U/C đã tổng hợp",
        "Nhập từng chỉ báo từ bảng hỏi"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("**Gợi ý:** Nếu bạn đã tính trung bình từng lớp từ bảng hỏi, chọn chế độ đầu tiên.")


# =========================
# Input mode 1: Direct layer scores
# =========================

if input_mode == "Nhập điểm lớp K/A/U/C đã tổng hợp":
    st.subheader("Nhập điểm tổng hợp cho từng lớp KAUC")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        K = st.number_input(
            "Knowledge – K",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1
        )

    with col2:
        A = st.number_input(
            "Action – A",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1
        )

    with col3:
        U = st.number_input(
            "Utility – U",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1
        )

    with col4:
        C = st.number_input(
            "Contribution – C",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1
        )


# =========================
# Input mode 2: Indicator-level scores
# =========================

else:
    st.subheader("Nhập điểm từng chỉ báo trong bảng hỏi")

    st.info(
        "Mỗi lớp có thể có nhiều câu hỏi/chỉ báo. "
        "App sẽ tự tính trung bình để ra điểm K, A, U, C."
    )

    col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)

    with col_cfg1:
        n_K = st.number_input("Số chỉ báo Knowledge", min_value=1, max_value=20, value=3, step=1)

    with col_cfg2:
        n_A = st.number_input("Số chỉ báo Action", min_value=1, max_value=20, value=3, step=1)

    with col_cfg3:
        n_U = st.number_input("Số chỉ báo Utility", min_value=1, max_value=20, value=3, step=1)

    with col_cfg4:
        n_C = st.number_input("Số chỉ báo Contribution", min_value=1, max_value=20, value=3, step=1)

    st.markdown("### Knowledge indicators")
    K_values = []
    cols = st.columns(min(n_K, 5))
    for i in range(n_K):
        with cols[i % len(cols)]:
            value = st.number_input(
                f"K{i+1}",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
                key=f"K_{i}"
            )
            K_values.append(value)

    st.markdown("### Action indicators")
    A_values = []
    cols = st.columns(min(n_A, 5))
    for i in range(n_A):
        with cols[i % len(cols)]:
            value = st.number_input(
                f"A{i+1}",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
                key=f"A_{i}"
            )
            A_values.append(value)

    st.markdown("### Utility indicators")
    U_values = []
    cols = st.columns(min(n_U, 5))
    for i in range(n_U):
        with cols[i % len(cols)]:
            value = st.number_input(
                f"U{i+1}",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
                key=f"U_{i}"
            )
            U_values.append(value)

    st.markdown("### Contribution indicators")
    C_values = []
    cols = st.columns(min(n_C, 5))
    for i in range(n_C):
        with cols[i % len(cols)]:
            value = st.number_input(
                f"C{i+1}",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
                key=f"C_{i}"
            )
            C_values.append(value)

    K = mean_layer_score(K_values)
    A = mean_layer_score(A_values)
    U = mean_layer_score(U_values)
    C = mean_layer_score(C_values)

    st.markdown("### Điểm trung bình từng lớp")
    st.dataframe(
        pd.DataFrame({
            "Layer": ["Knowledge", "Action", "Utility", "Contribution"],
            "Score": [K, A, U, C]
        }),
        use_container_width=True
    )


# =========================
# Calculation
# =========================

st.divider()

if st.button("Tính KCI", type="primary"):
    result = calculate_kci(K, A, U, C, tau=tau)

    st.subheader("Kết quả tính toán")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("KCI weighted", f"{result['KCI_weighted']:.2f}")

    with metric_col2:
        st.metric("KCI equal-weight", f"{result['KCI_equal']:.2f}")

    with metric_col3:
        st.metric("Vertical maturity – VM", f"{result['VM']:.2f}")

    with metric_col4:
        st.metric("Maturity stage m", f"{result['m']}/4")

    st.markdown("### Bảng chi tiết")

    detail_df = pd.DataFrame({
        "Component": [
            "K",
            "A",
            "U",
            "C",
            "k = (K-1)/4",
            "a = (A-1)/4",
            "u = (U-1)/4",
            "c = (C-1)/4",
            "HI weighted",
            "HI equal-weight",
            "VM",
            "KCI weighted",
            "KCI equal-weight",
            "Simple normalized average"
        ],
        "Value": [
            result["K"],
            result["A"],
            result["U"],
            result["C"],
            result["k"],
            result["a"],
            result["u"],
            result["c"],
            result["HI_weighted"],
            result["HI_equal"],
            result["VM"],
            result["KCI_weighted"],
            result["KCI_equal"],
            result["simple_normalized_average"]
        ]
    })

    st.dataframe(detail_df, use_container_width=True)

    st.markdown("### Chẩn đoán bottleneck")

    st.write(f"**Bottleneck:** {result['bottleneck']}")
    st.write(f"**Giải thích:** {result['interpretation']}")

    profile_df = pd.DataFrame({
        "Layer": ["Knowledge", "Action", "Utility", "Contribution"],
        "Raw score": [result["K"], result["A"], result["U"], result["C"]],
        "Normalized score": [result["k"], result["a"], result["u"], result["c"]],
        "Pass threshold?": [
            result["K"] >= tau,
            result["A"] >= tau,
            result["U"] >= tau,
            result["C"] >= tau
        ]
    })

    st.markdown("### KAUC profile")
    st.dataframe(profile_df, use_container_width=True)

    st.bar_chart(
        profile_df.set_index("Layer")[["Raw score"]]
    )

    # Export result
    export_df = pd.DataFrame([result])
    csv = export_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Tải kết quả CSV",
        data=csv,
        file_name="kci_result.csv",
        mime="text/csv"
    )

else:
    st.warning("Nhập điểm và bấm **Tính KCI** để xem kết quả.")