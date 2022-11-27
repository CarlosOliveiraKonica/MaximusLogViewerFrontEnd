from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

from common.tables import ExpositionTable

if __name__ == "__main__":
    
    import streamlit as st
    
    file = r"D:\Dudu\Arquivos de empregos anteriores\Konica\MaximusLogViewer\GENERATOR_LOGS\2022-11-15 08h37m02s - ExportedData.xlsx"
    table = ExpositionTable()
    table.set_file(file)
    df = table.get_dataframe()
    df = df.drop(df[df["Exposição"] == "TOTAL"].index)
    df = df.drop(df[df["mA"] == 48641].index)
    
    print(df)
    
    df2 = df.groupby(['mAs', 'kV'], as_index=False).sum()
    print(df2)
    
    fig = plt.figure()
    ax = Axes3D(fig)
    
    x = df["mAs"]
    y = df["kV"]
    z = np.zeros(len(x))
    
    dx = np.ones(len(x))
    dy = np.ones(len(x))
    dz = df["TOTAL"]
    
    ax.bar3d(x, y, z, dx, dy, dz, shade=True)
    ax.set_xlabel("mAs")
    ax.set_ylabel("kV")
    ax.set_zlabel("TOTAL")
    
    st.pyplot(fig)
    plt.show()
