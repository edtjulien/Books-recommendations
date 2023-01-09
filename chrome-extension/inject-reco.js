// https://www.cssscript.com/google-style-draggable-modal-window-with-pure-javascript/

const DEFAULT_WEIGHT = {
    "tag_": 0,
    "sen_": 50,
    "users": 0,
    "jaccard": 50,
    "book_rating_value": 10,
    "book_nb_comm": 0,
    "book_rating_count": 0
}

const MOOKUP = [
    {
        "title": "La guerre des clans, Cycle I - La guerre des clans, tome 3 : Les mystères de la forêt",
        "url": "https://www.babelio.com/livres/Hunter-La-guerre-des-clans-Cycle-I-La-guerre-des-clans-/74492",
        "image": "https://images-na.ssl-images-amazon.com/images/I/41BEswhX8SL._SX210_.jpg",
        "author": "Hunter Erin",
        "author_url": "/auteur/Erin-Hunter/39403",
        "book_rating_value": 4.34,
        "book_rating_count": 621,
        "score": "0.922946901482088"
    },
    {
        "title": "La tyrannie de l'arc-en-ciel",
        "url": "https://www.babelio.com/livres/Fforde-La-tyrannie-de-larc-en-ciel/710930",
        "image": "https://images-na.ssl-images-amazon.com/images/I/41RRD8wsQ8L._SX210_.jpg",
        "author": "Fforde Jasper",
        "author_url": "/auteur/Jasper-Fforde/3537",
        "book_rating_value": 4.1,
        "book_rating_count": 176,
        "score": "0.9226500912319447"
    },
    {
        "title": "Just Kids",
        "url": "https://www.babelio.com/livres/Smith-Just-Kids/213395",
        "image": "https://images-na.ssl-images-amazon.com/images/I/41ndJ93XM2L._SX210_.jpg",
        "author": "Smith Patti",
        "author_url": "/auteur/Patti-Smith/79391",
        "book_rating_value": 4.22,
        "book_rating_count": 1040,
        "score": "0.9219455558988402"
    },
    {
        "title": "Delirium, Tome 1",
        "url": "https://www.babelio.com/livres/Oliver-Delirium-Tome-1/217552",
        "image": "/couv/CVT_CVT_Delirium-Tome-1_2078.jpg",
        "author": "Oliver Lauren",
        "author_url": "/auteur/Lauren-Oliver/115308",
        "book_rating_value": 3.94,
        "book_rating_count": 1462,
        "score": "0.9202627768947241"
    },
    {
        "title": "Chroniques de Zombieland, tome 1 : Alice au pays des Zombies",
        "url": "https://www.babelio.com/livres/Showalter-Chroniques-de-Zombieland-tome-1--Alice-au-pays-de/469495",
        "image": "/images/couv-defaut-grande.jpg",
        "author": "Showalter Gena",
        "author_url": "/auteur/Gena-Showalter/10049",
        "book_rating_value": 4.06,
        "book_rating_count": 325,
        "score": "0.9126119177216623"
    },
    {
        "title": "La Tour Sombre, Tome 4 : Magie et cristal",
        "url": "https://www.babelio.com/livres/King-La-Tour-Sombre-Tome-4--Magie-et-cristal/5459",
        "image": "https://images-na.ssl-images-amazon.com/images/I/51kJqYNikhL._SX210_.jpg",
        "author": "King Stephen",
        "author_url": "/auteur/Stephen-King/3933",
        "book_rating_value": 4.2,
        "book_rating_count": 655,
        "score": "0.9091295714693041"
    },
    {
        "title": "Les Misérables, tome 1",
        "url": "https://www.babelio.com/livres/Hugo-Les-Miserables-tome-1/1171044",
        "image": "https://images-na.ssl-images-amazon.com/images/I/41s1JTtwO5L._SX210_.jpg",
        "author": "Hugo Victor",
        "author_url": "/auteur/Victor-Hugo/2250",
        "book_rating_value": 4.32,
        "book_rating_count": 6236,
        "score": "0.9090452714697298"
    },
    {
        "title": "La Souris Bleue",
        "url": "https://www.babelio.com/livres/Atkinson-La-Souris-Bleue/8973",
        "image": "https://images-na.ssl-images-amazon.com/images/I/51-xQL0Lh7L._SX210_.jpg",
        "author": "Atkinson Kate",
        "author_url": "/auteur/Kate-Atkinson/7351",
        "book_rating_value": 3.75,
        "book_rating_count": 518,
        "score": "0.908801383731081"
    },
    {
        "title": "Une bouche sans personne",
        "url": "https://www.babelio.com/livres/Marchand-Une-bouche-sans-personne/855482",
        "image": "/couv/CVT_Une-bouche-sans-personne_102.jpg",
        "author": "Marchand Gilles",
        "author_url": "/auteur/Gilles-Marchand/103619",
        "book_rating_value": 3.82,
        "book_rating_count": 310,
        "score": "0.9079598519649804"
    },
    {
        "title": "H2G2, tome 1 : Le Guide du voyageur galactique",
        "url": "https://www.babelio.com/livres/Adams-H2G2-tome-1--Le-Guide-du-voyageur-galactique/6617",
        "image": "/couv/CVT_cvt_Le-Guide-du-voyageur-galactique--Tome-1-H2G2_1769.jpg",
        "author": "Adams Douglas",
        "author_url": "/auteur/Douglas-Adams/2627",
        "book_rating_value": 3.91,
        "book_rating_count": 1828,
        "score": "0.9078444456653786"
    }
]

let currentWeight = DEFAULT_WEIGHT
const sessionWeight = window.sessionStorage.getItem("currentWeight");
if (sessionWeight)
    currentWeight = JSON.parse(sessionWeight)

function idBookPage() {
    const item = document.querySelector("div.livre_header_con h1 a");
    if (item) {
        if (item.href.indexOf('/livres/') !== -1)
            return item.href.split('/').at(-1);
        else return 0;
    }
    return 0;
}
window.sessionStorage.clear()
function getData() {
    const idBook = idBookPage()
    if (idBook === 0)
        return;

    const sessionWeight = window.sessionStorage.getItem("currentWeight");
    if (sessionWeight)
        currentWeight = JSON.parse(sessionWeight)

    // fetch(`https://api.mldatago.com/?id=${idBook}`, {
    //     method: 'GET', // *GET, POST, PUT, DELETE, etc.
    //     mode: 'cors', // no-cors, *cors, same-origin
    // })
    // fetch(`https://api.mldatago.com/`, {
    fetch(`http://localhost:8000/`, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "id": idBook, "weights": currentWeight }) // body data type must match "Content-Type" header
    })
        .then(response => {
            return response.json();
        })
        .then(json => {
            createHTML(json['message'].slice(0, 5));
            createHTMLWeights()
        });
}

function createBookHTML(book) {

    const { url, title, image, author, author_url } = book;

    return `
    <div class="col col-2-4 list_livre" style="max-width:120px;overflow: visible;" itemscope="" itemtype="http://schema.org/Book">
        <a href="${url}">
        <img loading="lazy" src="${image}" alt="${title}" title="${title}" onerror="this.onerror=null;this.src='/images/couv-defaut.jpg';">
        <h2 itemprop="name" style="">${title}</h2>
        </a>
        <a href="${author_url}">
        <h3 style="margin:0px">${author}</h3>
        </a>
        <h3 style="margin:5px 0 0 0"></h3>
    </div>
 `;
}

function createHTML(books) {

    const area = document.getElementById("reco_area")
    if (area)
        area.remove()

    const divMain = document.getElementsByClassName("livre_con")[0];
    const divReco = document.createElement("div");
    divReco.setAttribute('id', "reco_area");

    const bookHtml = books.map((book) => createBookHTML(book));

    divReco.innerHTML = `
    <style>
    .reco_title {
        display:flex;
        justify-content:space-between;
    }
    .reco_title button {
        display:flex;
        align-items:center;
        justify-content:center;
        margin-right:20px;
        width:35px;
        padding:1px;
        background:#EAE7DF;
        border:1px solid #888A;
        border-radius:5px;
    }
    .reco_title button:hover {
        background:#DCD5C8;
    }
    .reco_title button img {
        width:20px;
        height:25px;
    }
    </style>
    <div class="titre reco_title">
        <div>Recommandations liées à cette lecture</div>
        <button id="reco_button" class="icon"><img src="${chrome.runtime.getURL('parameter.svg')}" /></button>
    </div>
    <div class="list_livre_con">${bookHtml}</div>`;

    divMain.after(divReco);

    document.getElementById("reco_button").onclick = function () {
        document.getElementById("bookreco_weights").style.display = "";
    }

}
function createHTMLWeights() {

    const divMain = document.getElementsByClassName("livre_con")[0];
    const divWeights = document.createElement("div");

    divWeights.innerHTML = `
    <style>
    #bookreco_weights {
        position:absolute;
        width:500px;
        height:450px;
        background-color:#000D;
        z-index:9999;
        padding:30px;
        border-radius:10px;
        transform: translate(110px, 50px);
        color:#FFF;
        transition: opacity 0.6s linear;
    }
    .bookreco_title {
        font-weight:bold;
        font-size:16px;
        margin-bottom:20px;
    }
    .bookreco_param {
        margin-top:20px;
    }
    .bookreco_param label {
        display:block;
        font-weight:bold;
        margin-bottom:5px;
    }
    .bookreco_param input[type='range'] {
        width:250px;
    }

    #bookreco_button {
        display:block;
        margin: 0 auto 0 auto;
        width:200px;
        padding:10px;
        margin-top:40px;
        color:#000;
    }
    </style>
    <div id="bookreco_weights" style="display:none;">
        <div class='bookreco_title'>Paramètres du modèle de recommandations :</div>
        <div class="bookreco_param">
            <label for="sen_">Sentiments :</label>
            <input type="range" id="sen_" name="sen_" min="0" max="100" value="${currentWeight["sen_"]}">
        </div>
        <div class="bookreco_param">
            <label for="jaccard">Similarité vocabulaire :</label>
            <input type="range" id="jaccard" name="jaccard" min="0" max="100" value="${currentWeight["jaccard"]}">
        </div>
        <div class="bookreco_param">
            <label for="tags_">Thèmes :</label>
            <input type="range" id="tag_" name="tags_" min="0" max="100" value="${currentWeight["tag_"]}">
        </div>
        <div class="bookreco_param">
            <label for="book_rating_value">Notes :</label>
            <input type="range" id="book_rating_value" name="book_rating_value" min="0" max="100" value="${currentWeight["book_rating_value"]}">
        </div>
        <button id="bookreco_button">Mettre à jour</button>
    </div>`;

    divMain.after(divWeights);

    document.getElementById("bookreco_button").onclick = function () {
        document.getElementById("bookreco_weights").style.display = "none";

        currentWeight["sen_"] = parseInt(document.getElementById("sen_").value);
        currentWeight["tag_"] = parseInt(document.getElementById("tag_").value);
        currentWeight["jaccard"] = parseInt(document.getElementById("jaccard").value);
        currentWeight["book_rating_value"] = parseInt(document.getElementById("book_rating_value").value);

        window.sessionStorage.setItem("currentWeight", JSON.stringify(currentWeight));

        getData();
    }
}

getData();