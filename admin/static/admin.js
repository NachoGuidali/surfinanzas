// Panel del blog — editor, vista previa, portada y confirmaciones.
(function () {
  "use strict";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };
  var csrf = function () {
    var campo = $('input[name="csrf"]');
    return campo ? campo.value : "";
  };

  /* --------------------------------------------------------------
     Confirmación antes de eliminar
     -------------------------------------------------------------- */
  $$("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirmar)) e.preventDefault();
    });
  });

  var cuerpo = $("#cuerpo");
  if (!cuerpo) return;   // el resto solo aplica al editor

  var form = $("#form-nota");
  var URL_PREVIEW = form.dataset.urlPreview;
  var URL_IMAGEN = form.dataset.urlImagen;
  var urlMedia = function (ruta) {
    return form.dataset.urlMedia.replace("__X__", encodeURIComponent(ruta.split("/").pop()));
  };
  var titulo = $("#titulo");
  var slug = $("#slug");
  var resumen = $("#resumen");
  var sucio = false;

  /* --------------------------------------------------------------
     Guardar: registra qué botón se apretó
     -------------------------------------------------------------- */
  $$("button[data-accion]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      $("#accion").value = btn.dataset.accion;
      sucio = false;   // no avisar al salir: lo estamos guardando
    });
  });

  form.addEventListener("input", function () { sucio = true; });
  window.addEventListener("beforeunload", function (e) {
    if (!sucio) return;
    e.preventDefault();
    e.returnValue = "";
  });

  // Ctrl/Cmd + S guarda borrador
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      $("#accion").value = "borrador";
      sucio = false;
      form.submit();
    }
  });

  /* --------------------------------------------------------------
     Slug automático a partir del título
     -------------------------------------------------------------- */
  function slugificar(texto) {
    return (texto || "")
      .normalize("NFKD").replace(/[̀-ͯ]/g, "")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "").replace(/-{2,}/g, "-").slice(0, 80);
  }

  var slugManual = slug.value.trim() !== "";
  slug.addEventListener("input", function () { slugManual = true; });
  slug.addEventListener("blur", function () { slug.value = slugificar(slug.value); });
  titulo.addEventListener("input", function () {
    if (!slugManual) slug.value = slugificar(titulo.value);
  });

  /* --------------------------------------------------------------
     Contadores
     -------------------------------------------------------------- */
  function contar() {
    var palabras = (cuerpo.value.match(/\S+/g) || []).length;
    $("#cuenta-palabras").textContent = palabras;
    $("#cuenta-minutos").textContent = Math.max(1, Math.round(palabras / 200));
    $("#cuenta-resumen").textContent = resumen.value.length;
  }
  cuerpo.addEventListener("input", contar);
  resumen.addEventListener("input", contar);
  contar();

  /* --------------------------------------------------------------
     Barra de formato Markdown
     -------------------------------------------------------------- */
  function envolver(antes, despues, textoPorDefecto) {
    var ini = cuerpo.selectionStart, fin = cuerpo.selectionEnd;
    var sel = cuerpo.value.slice(ini, fin) || textoPorDefecto || "";
    var nuevo = antes + sel + (despues || "");
    cuerpo.setRangeText(nuevo, ini, fin, "end");
    if (!cuerpo.value.slice(ini, fin)) {
      cuerpo.selectionStart = ini + antes.length;
      cuerpo.selectionEnd = ini + antes.length + sel.length;
    }
    cuerpo.focus();
    contar();
    sucio = true;
  }

  function prefijarLineas(prefijo, numerada) {
    var ini = cuerpo.selectionStart, fin = cuerpo.selectionEnd;
    var inicioLinea = cuerpo.value.lastIndexOf("\n", ini - 1) + 1;
    var finLinea = cuerpo.value.indexOf("\n", fin);
    if (finLinea === -1) finLinea = cuerpo.value.length;

    var bloque = cuerpo.value.slice(inicioLinea, finLinea) || "Texto";
    var salida = bloque.split("\n").map(function (linea, i) {
      return (numerada ? (i + 1) + ". " : prefijo) + linea.replace(/^([#>\-\s]|\d+\.\s)+/, "");
    }).join("\n");

    cuerpo.setRangeText(salida, inicioLinea, finLinea, "end");
    cuerpo.focus();
    contar();
    sucio = true;
  }

  var acciones = {
    negrita: function () { envolver("**", "**", "texto"); },
    cursiva: function () { envolver("*", "*", "texto"); },
    h2: function () { prefijarLineas("## "); },
    h3: function () { prefijarLineas("### "); },
    lista: function () { prefijarLineas("- "); },
    numerada: function () { prefijarLineas("", true); },
    cita: function () { prefijarLineas("> "); },
    link: function () {
      var url = window.prompt("¿A qué dirección apunta el enlace?", "https://");
      if (url) envolver("[", "](" + url + ")", "texto del enlace");
    },
    imagen: function () {
      var entrada = $("#archivo-portada");
      if (entrada) { entrada.dataset.destino = "cuerpo"; entrada.click(); }
    }
  };

  $$(".btn-md[data-md]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var fn = acciones[btn.dataset.md];
      if (fn) fn();
    });
  });

  /* --------------------------------------------------------------
     Vista previa (la renderiza el servidor: coincide con el resultado)
     -------------------------------------------------------------- */
  var botonPreview = $("#ver-preview");
  var panelPreview = $("#preview");
  var htmlPreview = $("#preview-html");
  var temporizador = null;
  var ultimoTexto = null;

  function pedirPreview() {
    if (panelPreview.hidden || cuerpo.value === ultimoTexto) return;
    ultimoTexto = cuerpo.value;
    fetch(URL_PREVIEW, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() },
      body: JSON.stringify({ cuerpo: cuerpo.value })
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
      .then(function (d) { htmlPreview.innerHTML = d.html; })
      .catch(function () {
        htmlPreview.textContent = "No se pudo generar la vista previa.";
      });
  }

  botonPreview.addEventListener("click", function () {
    var abierto = panelPreview.hidden;
    panelPreview.hidden = !abierto;
    botonPreview.setAttribute("aria-pressed", String(abierto));
    if (abierto) pedirPreview();
  });

  cuerpo.addEventListener("input", function () {
    window.clearTimeout(temporizador);
    temporizador = window.setTimeout(pedirPreview, 600);
  });

  /* --------------------------------------------------------------
     Portada: subir, arrastrar, elegir de la galería, quitar
     -------------------------------------------------------------- */
  var entradaArchivo = $("#archivo-portada");
  var campoImagen = $("#imagen");
  var imgPortada = $("#portada-img");
  var vaciaPortada = $("#portada-vacia");
  var zona = $("#portada");
  var botonQuitar = $("#quitar-portada");

  function mostrarPortada(ruta) {
    campoImagen.value = ruta || "";
    if (ruta) {
      imgPortada.src = urlMedia(ruta) + "?t=" + Date.now();
      imgPortada.hidden = false;
      vaciaPortada.hidden = true;
      botonQuitar.hidden = false;
    } else {
      imgPortada.removeAttribute("src");
      imgPortada.hidden = true;
      vaciaPortada.hidden = false;
      botonQuitar.hidden = true;
    }
    sucio = true;
  }

  function subir(archivo, destino) {
    if (!archivo) return;
    var datos = new FormData();
    datos.append("imagen", archivo);
    zona.classList.add("arrastrando");
    fetch(URL_IMAGEN, {
      method: "POST",
      headers: { "X-CSRF-Token": csrf() },
      body: datos
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.d.error || "No se pudo subir la imagen.");
        if (destino === "cuerpo") {
          envolver("![", "](../" + res.d.ruta + ")", "descripción de la imagen");
        } else {
          mostrarPortada(res.d.ruta);
        }
      })
      .catch(function (err) { window.alert(err.message); })
      .then(function () { zona.classList.remove("arrastrando"); });
  }

  entradaArchivo.addEventListener("change", function () {
    var destino = entradaArchivo.dataset.destino || "portada";
    subir(entradaArchivo.files[0], destino);
    entradaArchivo.value = "";
    delete entradaArchivo.dataset.destino;
  });

  ["dragenter", "dragover"].forEach(function (ev) {
    zona.addEventListener(ev, function (e) {
      e.preventDefault();
      zona.classList.add("arrastrando");
    });
  });
  ["dragleave", "drop"].forEach(function (ev) {
    zona.addEventListener(ev, function (e) {
      e.preventDefault();
      zona.classList.remove("arrastrando");
    });
  });
  zona.addEventListener("drop", function (e) {
    if (e.dataTransfer && e.dataTransfer.files.length) subir(e.dataTransfer.files[0], "portada");
  });

  botonQuitar.addEventListener("click", function () { mostrarPortada(""); });

  $$(".galeria-item").forEach(function (btn) {
    btn.addEventListener("click", function () { mostrarPortada(btn.dataset.ruta); });
  });

  /* --------------------------------------------------------------
     Simulador: vista previa en vivo mientras se editan los valores
     -------------------------------------------------------------- */
  var formSim = $("#form-simulador");
  if (formSim) {
    var campos = {
      tasa: $("#tasa"), inicial: $("#inicial"), plazoInicial: $("#plazo_inicial"),
      minimo: $("#minimo"), maximo: $("#maximo")
    };
    var salida = {
      monto: $("#pv-monto"), plazo: $("#pv-plazo"), cuota: $("#pv-cuota"),
      total: $("#pv-total"), costo: $("#pv-costo")
    };

    var numero = function (input) {
      if (!input) return NaN;
      return parseFloat(String(input.value).replace(/\./g, "").replace(",", "."));
    };
    var pesos = function (n) {
      return isFinite(n) ? "$ " + Math.round(n).toLocaleString("es-AR") : "—";
    };

    var recalcular = function () {
      var tasa = parseFloat(String(campos.tasa.value).replace(",", ".")) / 100;
      var capital = numero(campos.inicial);
      var plazo = parseInt(campos.plazoInicial.value, 10);

      if (!isFinite(capital) || !isFinite(plazo) || plazo < 1 || !isFinite(tasa) || tasa < 0) {
        Object.keys(salida).forEach(function (k) {
          if (salida[k]) salida[k].textContent = "—";
        });
        return;
      }

      var cuota = tasa > 0
        ? capital * tasa / (1 - Math.pow(1 + tasa, -plazo))
        : capital / plazo;
      var total = cuota * plazo;

      salida.monto.textContent = pesos(capital);
      salida.plazo.textContent = plazo + " meses";
      salida.cuota.textContent = pesos(cuota);
      salida.total.textContent = pesos(total);
      salida.costo.textContent = pesos(total - capital) +
        "  (" + Math.round(((total / capital) - 1) * 100) + "%)";
    };

    Object.keys(campos).forEach(function (k) {
      if (campos[k]) campos[k].addEventListener("input", recalcular);
    });
    recalcular();
  }
})();
