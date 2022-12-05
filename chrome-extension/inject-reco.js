// https://www.cssscript.com/google-style-draggable-modal-window-with-pure-javascript/

const MOCKUP = [
    {
        title : "Fils de personne",
        url : "/livres/Pasques-Fils-de-personne/1466172",
        image : "https://m.media-amazon.com/images/I/51FlwT9EH2L._SX95_.jpg",
        author : "Jean-François Pasques",
    },
    {
        title : "La fille qui s’échappa d’Auschwitz",
        url : "/livres/Midwood-La-fille-qui-sechappa-dAuschwitz/1463048",
        image : "/couv/cvt_La-fille-qui-sechappa-dAuschwitz_8134.jpg",
        author : "Ellie Midwood",
    },
    {
        title : "Maple",
        url : "/livres/Goudreault-Maple/1467288",
        image : "https://m.media-amazon.com/images/I/41px-RwRutL._SX95_.jpg",
        author : "David Goudreault",
    },
    {
        title : "1629, Les Naufragés du Jakarta, tome 1 : L'apothicaire du Diable",
        url : "/livres/Dorison-1629-Les-Naufrages-du-Jakarta-tome-1--Lapothicai/1446523",
        image : "/couv/cvt_1629-Les-Naufrages-du-Jakarta-tome-1--Lapothicai_566.jpg",
        author : "Xavier Dorison",
    },
    {
        title : "Une saison pour les ombres",
        url : "/livres/Ellory-Une-saison-pour-les-ombres/1466915",
        image : "/couv/cvt_Une-saison-pour-les-ombres_145.jpg",
        author : "R. J. Ellory",
    },
]

// Example POST method implementation:
async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
      method: 'GET', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, *cors, same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json'
        // 'Content-Type': 'application/x-www-form-urlencoded',
      },
      redirect: 'follow', // manual, *follow, error
      referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      //body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
  }

function isBookPage() {
    const item = document.querySelector("div.livre_header_con h1 a");
    if(item) {
        if(item.href.indexOf('/livres/') !== -1)
            return true;
        else return false;
    }
    return false;
}

function getData() {
    if(!isBookPage())
        return;

    // console.log("BBBBook page :", window.location.href)


    fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
    // fetch('http://mldatago.com:8000/?id=1829', {
    //     method: 'GET', // *GET, POST, PUT, DELETE, etc.
    //     mode: 'no-cors', // no-cors, *cors, same-origin
    // })
    .then(data => {
        return data;
    })
    .then(post => {
        //console.log(post)

        // console.log(post);
        createHTML(MOCKUP);
    });
}

function createBookHTML(book) {

    const { url, title, image, author } = book;

    return `
    <div class="col col-2-4 list_livre" style="max-width:120px;overflow: visible;" itemscope="" itemtype="http://schema.org/Book">
        <a href="${url}">
        <img loading="lazy" src="${image}" alt="${title}" title="${title}" onerror="this.onerror=null;this.src='/images/couv-defaut.jpg';">
        <h2 itemprop="name" style="">${title}</h2>
        </a>
        <!--<a href="#">-->
        <h3 style="margin:0px">${author}</h3>
        <!--</a>-->
        <h3 style="margin:5px 0 0 0"></h3>
    </div>
 `;
}

function createHTML(books) {

    const divMain = document.getElementsByClassName("livre_con")[0];
    const divReco = document.createElement("div");

    const bookHtml = books.map((book) => createBookHTML(book));

    divReco.innerHTML = `
    <div class="titre">
        Recommandations liées à cette lecture
    </div>
    <div class="list_livre_con">${bookHtml}</div>`;

    divMain.after(divReco);

}

getData()