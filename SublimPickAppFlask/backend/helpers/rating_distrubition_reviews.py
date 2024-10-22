import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Helper function to generate review distribution graph
def create_review_graphs(product_reviews):
    # Vérifier s'il y a des reviews
    if not product_reviews or len(product_reviews) == 0:
        # Si pas de critiques, retourner un message par défaut ou un graphique vide
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Distribution of Star Ratings')
        ax.axis('off')  # Enlever les axes

        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close(fig)  # Fermer la figure pour libérer la mémoire
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return plot_url
    
    # Si des reviews existent, continuer avec le traitement
    df = pd.DataFrame(product_reviews)
    df['review_date'] = pd.to_datetime(df['review_date'],  format='%m/%d/%y', errors='coerce')

    df_sorted = df.sort_values(by='review_date', ascending=False)
    star_counts = df_sorted['review_stars'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Utiliser une palette de couleurs personnalisée (Set3)
    colors = plt.get_cmap("Dark2").colors  # Changez la palette ici

    # Générer le camembert sans pourcentage
    wedges, texts = ax.pie(star_counts, startangle=90, colors=colors[:len(star_counts)])

    # Ajouter une légende avec les pourcentages à l'extérieur du camembert
    labels = [f"{int(star)} stars: {count} ({(count / star_counts.sum()) * 100:.1f}%)" for star, count in zip(star_counts.index, star_counts)]
    ax.legend(wedges, labels, title="Star Ratings", loc="center left", bbox_to_anchor=(1, 0.5))

    ax.set_title('Distribution of Star Ratings')

    # Sauvegarder le graphique en image
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')  # 'bbox_inches' to ensure the legend is included
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.close(fig)  # Fermer la figure pour libérer la mémoire
    return plot_url



# import pandas as pd
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO

# # Helper function to generate review distribution graph
# def create_review_graphs(product_reviews):
#     # Vérifier s'il y a des reviews
#     if not product_reviews or len(product_reviews) == 0:
#         # Si pas de critiques, retourner un message par défaut ou un graphique vide
#         fig, ax = plt.subplots(figsize=(5, 5))
#         ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
#         ax.set_title('Distribution of Star Ratings')
#         ax.axis('off')  # Enlever les axes

#         img = BytesIO()
#         plt.savefig(img, format='png')
#         # After saving
#         plt.close(fig)  # This will close the figure and free memory
#         img.seek(0)
#         plot_url = base64.b64encode(img.getvalue()).decode()
#         return plot_url
    
#     # Si des reviews existent, continuer avec le traitement
#     df = pd.DataFrame(product_reviews)
#     df['review_date'] = pd.to_datetime(df['review_date'],  format='%m/%d/%y', errors='coerce')

#     df_sorted = df.sort_values(by='review_date', ascending=False)
#     star_counts = df_sorted['review_stars'].value_counts().sort_index()

#     fig, ax = plt.subplots(figsize=(5, 5))
#     ax.pie(star_counts, labels=star_counts.index, autopct='%1.1f%%', startangle=90)
#     ax.set_title('Distribution of Star Ratings')

#     img = BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode()
#     return plot_url