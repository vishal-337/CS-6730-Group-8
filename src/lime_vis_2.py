

import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from lime.lime_tabular import LimeTabularExplainer
import streamlit.components.v1 as components





@st.cache_data
def load_and_train(data_path: str):
    df = pd.read_csv(data_path)
    
    for c in df.columns:
        if c not in ['Origin','Destination','hs96']:
            df[c] = np.log1p(df[c])
    
    feature_cols = [
        c for c in df.columns
        if c not in ['Origin','Destination','hs96','2024']
    ]
    X = df[feature_cols]
    y = df['2024']
    
    rng = np.random.default_rng(42)
    idx = np.arange(len(X))
    rng.shuffle(idx)
    cut = int(0.8 * len(X))
    train_idx, test_idx = idx[:cut], idx[cut:]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    rf = RandomForestRegressor(n_estimators=5, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train)
    
    return df, test_idx, X_train, X_test, y_train, y_test, feature_cols, rf

def get_immigration_lime():
    st.title("Export Volume Prediction & LIME Explorer")
    data_path = os.path.join("data", "migration_trade_products_sci_df_hs96.csv")
    if not data_path:
        st.stop()
    
    df, test_idx, X_train, X_test, y_train, y_test, feature_cols, rf = load_and_train(data_path)
    r2 = rf.score(X_test, y_test)
    st.subheader("Model Performance")
    st.write(f"Test R²: **{r2:.3f}**")
    
    # importances = pd.Series(rf.feature_importances_, index=feature_cols)
    # importances = importances.sort_values(ascending=False)
    # st.subheader("Global Feature Importances")
    # fig_imp, ax_imp = plt.subplots()
    # importances.plot.bar(ax=ax_imp)
    # ax_imp.set_ylabel("Importance")
    # ax_imp.set_xlabel("Feature")
    # plt.tight_layout()
    # st.pyplot(fig_imp)
    # plt.clf()
    
    st.subheader("Local Explanation & Metadata")
    instance_idx = st.slider(
        "Select test-instance index",
        0, len(test_idx) - 1, 0
    )
    
    global_idx = test_idx[instance_idx]
    print(global_idx)
    origin      = df.loc[global_idx, 'Origin']
    destination = df.loc[global_idx, 'Destination']
    actual_exp  = df.loc[global_idx, 'export']        
    pred_log    = rf.predict(X_test.values[instance_idx].reshape(1, -1))[0]
    pred_exp    = np.expm1(pred_log)                  

    st.markdown(f"**Origin:** {origin}  ")
    st.markdown(f"**Destination:** {destination}  ")
    st.markdown(f"**Actual Export:** {actual_exp:,.0f}  ")
    st.markdown(f"**Predicted Export:** {pred_exp:,.0f}")
    
    print('feature_cols',feature_cols)  
    
    explainer = LimeTabularExplainer(
        training_data=X_train.values,
        feature_names=feature_cols,
        mode='regression',
        random_state=42
    )
    exp = explainer.explain_instance(
        data_row   = X_test.values[instance_idx],
        predict_fn = rf.predict,
        num_features = len(feature_cols)
    )
    
    
    exp_list   = exp.as_list() 
    print("exp_list",exp_list)
    feature_weights = list(exp.local_exp.values())[0]  
    feat_inds, weights = zip(*feature_weights)
    feat_names   = [feature_cols[i] for i in feat_inds]
    # feat_names = [desc.split(' ')[0] for desc, _ in exp_list]
    print("featnames",feat_names)
    weights    = [w for _, w in exp_list]
    print(X_test.iloc[instance_idx])
    actual_vals= [X_test.iloc[instance_idx][f] for f in feat_names]
    


    fig_lime, ax_lime = plt.subplots()
    y_pos = np.arange(len(feat_names))
    ax_lime.barh(y_pos, weights, align='center')
    ax_lime.set_yticks(y_pos)
    ax_lime.set_yticklabels(feat_names)
    ax_lime.invert_yaxis()
    ax_lime.set_xlabel("LIME Weight")
    ax_lime.set_title("LIME Feature Contributions")
    
    for i, (w, val) in enumerate(zip(weights, actual_vals)):
        ax_lime.text(w + np.sign(w)*0.01, i, f"{val:.2f}", va='center')
    

    components.html(exp.as_html(), height=800)
    # plt.tight_layout()
    # st.pyplot(fig_lime)
    # plt.clf()






