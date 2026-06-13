import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Genişlik Ayarı ve Başlık
st.set_page_config(page_title="Aile Bütçe Yönetimi", layout="wide", page_icon="💰")

st.title("👨‍👩‍👧‍👦 Aile Bütçe, Harcama ve Analiz Uygulaması")
st.write("Gelir ve giderlerinizi dinamik olarak yönetin, dairesel grafiklerle analiz edin.")

# Uygulama ilk açıldığında örnek verilerin yüklenmesi
if 'incomes' not in st.session_state:
    st.session_state.incomes = pd.DataFrame([
        {"Gelir Kalemi": "Koca Maaş", "Miktar (TL)": 50000.0},
        {"Gelir Kalemi": "Karı Maaş", "Miktar (TL)": 45000.0}
    ])

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame([
        {"Gider Kalemi": "Evim Sistemi Taksiti", "Kategori": "Ev/Kira", "Miktar (TL)": 15000.0},
        {"Gider Kalemi": "Kredi Kartı 1 Asgari/Toplam", "Kategori": "Kredi Kartı", "Miktar (TL)": 12000.0},
        {"Gider Kalemi": "Telefon Taksiti", "Kategori": "Taksitler", "Miktar (TL)": 3500.0},
        {"Gider Kalemi": "Market & Mutfak Alışverişi", "Kategori": "Mutfak/Gıda", "Miktar (TL)": 8000.0},
        {"Gider Kalemi": "Elektrik, Su, İnternet", "Kategori": "Faturalar", "Miktar (TL)": 4000.0},
        {"Gider Kalemi": "Araç Yakıt ve Bakım", "Kategori": "Ulaşım", "Miktar (TL)": 5000.0}
    ])

# Gider Kategorileri Listesi
categories = ["Kredi Kartı", "Taksitler", "Ev/Kira", "Mutfak/Gıda", "Faturalar", "Ulaşım", "Eğitim/Sağlık", "Diğer"]

# Arayüz Düzeni: Yan Yana İki Kolon (Gelirler ve Giderler)
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Gelirleriniz")
    st.info("💡 Tablonun altındaki boş satıra tıklayarak YENİ GELİR ekleyebilir, satırı seçip 'Delete' tuşu ile silebilirsiniz.")
    # Dinamik gelir tablosu editörü
    edited_incomes = st.data_editor(
        st.session_state.incomes, 
        num_rows="dynamic", 
        key="income_editor", 
        use_container_width=True
    )
    st.session_state.incomes = edited_incomes

with col2:
    st.subheader("📉 Giderleriniz")
    st.info("💡 Tablonun altından YENİ GIDER ekleyebilir, 'Kategori' sütunundan harcama türünü seçebilirsiniz.")
    
    # Gider tablosunda kategori seçimi için açılır kutu konfigürasyonu
    column_config = {
        "Kategori": st.column_config.SelectboxColumn(
            "Kategori",
            help="Gider grubunu seçin",
            options=categories,
            required=True,
        )
    }
    # Dinamik gider tablosu editörü
    edited_expenses = st.data_editor(
        st.session_state.expenses, 
        num_rows="dynamic", 
        column_config=column_config, 
        key="expense_editor", 
        use_container_width=True
    )
    st.session_state.expenses = edited_expenses

# Hesaplamaların Yapılması
total_income = edited_incomes["Miktar (TL)"].sum()
total_expense = edited_expenses["Miktar (TL)"].sum()
net_savings = total_income - total_expense
savings_rate = (net_savings / total_income) * 100 if total_income > 0 else 0

st.markdown("---")
st.header("📊 Anlık Durum Özeti ve Grafikler")

# Temel Gösterge Kartları (Metrics)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Toplam Aylık Gelir", f"{total_income:,.2f} TL")
m2.metric("Toplam Aylık Gider", f"{total_expense:,.2f} TL")
m3.metric("Aylık Kalan (Tasarruf)", f"{net_savings:,.2f} TL", delta=f"%{savings_rate:.1f} Tasarruf Oranı")
m4.metric("Tahmini Yıllık Birikim", f"{net_savings * 12:,.2f} TL")

st.write("")

# Grafik Alanı
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🍰 Gider Dağılımı (Dairesel Grafik)")
    if not edited_expenses.empty and total_expense > 0:
        # Kategorilere göre gruplayıp pasta grafiği çizme
        df_grouped = edited_expenses.groupby("Kategori")["Miktar (TL)"].sum().reset_index()
        fig_pie = px.pie(
            df_grouped, 
            values="Miktar (TL)", 
            names="Kategori", 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu,
            title="Harcamalarınızın Kategorisel Dağılımı"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Grafik üretilebilmesi için lütfen en az bir gider kalemi giriniz.")

with chart_col2:
    st.subheader("⚖️ Gelir ve Gider Dengesi")
    balance_df = pd.DataFrame({
        "Finansal Kalem": ["Toplam Gelir", "Toplam Gider"],
        "Miktar (TL)": [total_income, total_expense]
    })
    fig_bar = px.bar(
        balance_df, 
        x="Finansal Kalem", 
        y="Miktar (TL)", 
        color="Finansal Kalem",
        color_discrete_map={"Toplam Gelir": "#2ecc71", "Toplam Gider": "#e74c3c"},
        title="Gelir - Gider Karşılaştırma Grafiği"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.header("📅 Detaylı Aylık ve Yıllık Finansal Analiz")

tab1, tab2 = st.tabs(["🔍 Aylık Durum Analizi", "📈 1 Yıllık Gelecek Projeksiyonu"])

with tab1:
    st.subheader("Bu Ayın Finansal Sağlık Raporu")
    if net_savings > 0:
        st.success(f"🎉 Tebrikler! Bu ay bütçeniz artı veriyor. Gelirinizin %{savings_rate:.1f}'ini biriktirebiliyorsunuz.")
    elif net_savings == 0:
        st.warning("⚠️ Dikkat: Geliriniz giderlerinize tam ucu ucuna yetiyor! Acil durumlar için bütçenizde pay kalmadı.")
    else:
        st.error(f"🚨 Tehlike: Bütçeniz bu ay {abs(net_savings):,.2f} TL ekside! Kredi kartı veya borç yükünüzü azaltmayı düşünmelisiniz.")
        
    st.write("### 🔝 En Yüksek Harcama Kalemleriniz (Büyükten Küçüğe)")
    if not edited_expenses.empty:
        sorted_expenses = edited_expenses.sort_values(by="Miktar (TL)", ascending=False)
        st.dataframe(sorted_expenses, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🔮 12 Aylık Birikim Öngörüsü")
    st.write("Eğer her ay bu gelir ve harcama düzeniniz sabit kalırsa, 1 yıl içerisindeki toplam kümülatif birikim çizginiz şu şekilde olacaktır:")
    
    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    yearly_projection = []
    cumulative_sum = 0
    
    for m in months:
        cumulative_sum += net_savings
        yearly_projection.append({
            "Ay": m,
            "Aylık Gelir": total_income,
            "Aylık Gider": total_expense,
            "Net Aylık Birikim": net_savings,
            "Toplam Biriken Net Tutar": cumulative_sum
        })
        
    df_yearly = pd.DataFrame(yearly_projection)
    
    # Çizgi grafik ile yıllık kümülatif birikim gösterimi
    fig_line = px.line(
        df_yearly, 
        x="Ay", 
        y="Toplam Biriken Net Tutar", 
        markers=True, 
        title="12 Aylık Toplam Birikim Trendi",
        color_discrete_sequence=["#27ae60"]
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.write("### 📋 12 Aylık Detaylı Tablo Projeksiyonu")
    st.dataframe(df_yearly, use_container_width=True, hide_index=True)
