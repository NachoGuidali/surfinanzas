// ===================================================================
// Sur Finanzas — JS compartido
// Navbar, menú móvil, reveal on scroll, micro-interacciones, formularios.
// ===================================================================

(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  document.addEventListener("DOMContentLoaded", function () {

    /* ---------------------------------------------------------------
       Navbar: estado al hacer scroll + barra de progreso de lectura
       --------------------------------------------------------------- */
    var navbar = $(".navbar");
    var progress = $(".scroll-progress");
    var whatsapp = $(".whatsapp-float");
    var blobs = $$(".bg-blob");

    function onScroll() {
      var y = window.scrollY || document.documentElement.scrollTop;
      if (navbar) navbar.classList.toggle("is-scrolled", y > 12);

      if (progress) {
        var doc = document.documentElement;
        var max = doc.scrollHeight - window.innerHeight;
        progress.style.transform = "scaleX(" + (max > 0 ? Math.min(y / max, 1) : 0) + ")";
      }

      if (whatsapp) whatsapp.classList.toggle("is-visible", y > 220);
    }

    // Parallax sutil de los blobs decorativos de fondo
    function parallaxBlobs() {
      if (!blobs.length || reduceMotion) return;
      var y = window.scrollY || 0;
      blobs.forEach(function (b, i) {
        b.style.translate = "0 " + (y * (i % 2 === 0 ? 0.06 : -0.04)).toFixed(1) + "px";
      });
    }

    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        onScroll();
        parallaxBlobs();
        ticking = false;
      });
    }, { passive: true });

    /* ---------------------------------------------------------------
       Menú móvil
       --------------------------------------------------------------- */
    var toggle = $(".nav-toggle");
    var mobileMenu = $(".mobile-menu");

    if (toggle && mobileMenu) {
      // Índices para la entrada escalonada de los items
      $$("nav > *, .mobile-cta", mobileMenu).forEach(function (el, i) {
        el.style.setProperty("--i", i);
      });

      var setMenu = function (open) {
        mobileMenu.classList.toggle("open", open);
        toggle.setAttribute("aria-expanded", String(open));
        document.body.classList.toggle("menu-open", open);
      };

      toggle.addEventListener("click", function () {
        setMenu(!mobileMenu.classList.contains("open"));
      });

      // Cerrar al navegar
      $$("a, [data-close]", mobileMenu).forEach(function (el) {
        el.addEventListener("click", function () { setMenu(false); });
      });

      // Submenú de servicios (acordeón)
      $$(".mobile-sub-toggle", mobileMenu).forEach(function (btn) {
        var panel = btn.nextElementSibling;
        btn.addEventListener("click", function () {
          var open = btn.getAttribute("aria-expanded") === "true";
          btn.setAttribute("aria-expanded", String(!open));
          if (panel) panel.classList.toggle("open", !open);
        });
      });

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && mobileMenu.classList.contains("open")) {
          setMenu(false);
          toggle.focus();
        }
      });

      // Si se pasa a desktop con el menú abierto, cerrarlo
      window.matchMedia("(min-width: 1024px)").addEventListener("change", function (e) {
        if (e.matches) setMenu(false);
      });
    }

    /* ---------------------------------------------------------------
       Reveal on scroll (con stagger automático dentro de cada grilla)
       --------------------------------------------------------------- */
    var revealEls = $$("[data-reveal]");

    // Asigna un índice a cada elemento según su posición entre hermanos
    revealEls.forEach(function (el) {
      if (el.style.getPropertyValue("--reveal-delay")) return;
      var siblings = el.parentElement ? $$(":scope > [data-reveal]", el.parentElement) : [];
      if (siblings.length > 1) el.style.setProperty("--i", siblings.indexOf(el));
    });

    if (!reduceMotion && "IntersectionObserver" in window && revealEls.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("reveal");
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
      revealEls.forEach(function (el) { observer.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add("reveal"); });
    }

    /* ---------------------------------------------------------------
       Contadores animados: <span data-count="120" data-suffix="+">
       --------------------------------------------------------------- */
    var counters = $$("[data-count]");
    if (counters.length && "IntersectionObserver" in window) {
      var countObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          countObserver.unobserve(entry.target);
          animateCount(entry.target);
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { countObserver.observe(el); });
    }

    function animateCount(el) {
      var target = parseFloat(el.dataset.count) || 0;
      var suffix = el.dataset.suffix || "";
      var prefix = el.dataset.prefix || "";
      if (reduceMotion) {
        el.textContent = prefix + target.toLocaleString("es-AR") + suffix;
        return;
      }
      var duration = 1400;
      var start = performance.now();
      (function step(now) {
        var p = Math.min((now - start) / duration, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + Math.round(target * eased).toLocaleString("es-AR") + suffix;
        if (p < 1) requestAnimationFrame(step);
      })(start);
    }

    /* ---------------------------------------------------------------
       Tarjetas: luz que sigue al cursor + tilt 3D suave
       --------------------------------------------------------------- */
    var finePointer = window.matchMedia("(pointer: fine)").matches;
    if (finePointer && !reduceMotion) {
      $$(".card, .service-card").forEach(function (card) {
        card.classList.add("tilt");
        var raf = null;

        card.addEventListener("mousemove", function (e) {
          if (raf) return;
          raf = requestAnimationFrame(function () {
            var rect = card.getBoundingClientRect();
            var px = (e.clientX - rect.left) / rect.width;
            var py = (e.clientY - rect.top) / rect.height;
            card.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
            card.style.setProperty("--my", (py * 100).toFixed(1) + "%");
            var strength = 5;
            card.style.transform =
              "perspective(800px) rotateY(" + ((px - 0.5) * strength).toFixed(2) + "deg)" +
              " rotateX(" + ((0.5 - py) * strength).toFixed(2) + "deg) translateY(-4px)";
            raf = null;
          });
        });

        card.addEventListener("mouseleave", function () {
          card.style.transform = "";
        });
      });
    }

    /* ---------------------------------------------------------------
       Vídeos de fondo: autoplay tolerante a iOS y pausa fuera de pantalla
       --------------------------------------------------------------- */
    var videos = $$("video[autoplay]");
    var tryPlay = function (v) { var p = v.play(); if (p && p.catch) p.catch(function () {}); };
    videos.forEach(tryPlay);

    if (videos.length) {
      var resume = function () { videos.forEach(tryPlay); };
      document.addEventListener("touchstart", resume, { once: true, passive: true });
      document.addEventListener("click", resume, { once: true });

      if ("IntersectionObserver" in window) {
        var videoObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) tryPlay(entry.target);
            else entry.target.pause();
          });
        }, { threshold: 0.05 });
        videos.forEach(function (v) { videoObserver.observe(v); });
      }
    }

    /* ---------------------------------------------------------------
       Modal de contacto
       --------------------------------------------------------------- */
    var modalBackdrop = $("#modal-backdrop");
    var modalTitle = $("#modal-title");
    var modalSubtitle = $("#modal-subtitle");
    var modalForm = $("#modal-form");
    var lastFocused = null;

    var modalCopy = {
      demo: { title: "Solicitar una demo", subtitle: "Coordinamos una demo personalizada para tu equipo." },
      wallet: { title: "Quiero mi wallet", subtitle: "Contanos sobre tu negocio y te ayudamos a lanzarla." },
      contact: { title: "Hablemos", subtitle: "Dejanos tus datos y te contactamos a la brevedad." }
    };

    function openModal(kind) {
      if (!modalBackdrop) return;
      lastFocused = document.activeElement;
      var copy = modalCopy[kind] || modalCopy.contact;
      if (modalTitle) modalTitle.textContent = copy.title;
      if (modalSubtitle) modalSubtitle.textContent = copy.subtitle;
      if (modalForm) modalForm.dataset.kind = kind;
      modalBackdrop.classList.add("open");
      document.body.classList.add("menu-open");
      var first = modalBackdrop.querySelector("input, textarea, select");
      if (first) first.focus();
    }

    function closeModal() {
      if (!modalBackdrop) return;
      modalBackdrop.classList.remove("open");
      document.body.classList.remove("menu-open");
      if (lastFocused) lastFocused.focus();
    }

    $$("[data-open-modal]").forEach(function (btn) {
      btn.addEventListener("click", function () { openModal(btn.dataset.openModal); });
    });
    $$("[data-close-modal]").forEach(function (btn) {
      btn.addEventListener("click", closeModal);
    });
    if (modalBackdrop) {
      modalBackdrop.addEventListener("click", function (e) {
        if (e.target === modalBackdrop) closeModal();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeModal();
      });
    }

    /* ---------------------------------------------------------------
       Formularios: envío real contra /api/contacto
       --------------------------------------------------------------- */
    function limpiarErrores(form) {
      $$(".form-field.tiene-error", form).forEach(function (campo) {
        campo.classList.remove("tiene-error");
        var msg = campo.querySelector(".error-campo");
        if (msg) msg.remove();
      });
    }

    function marcarError(form, campo, texto) {
      var input = form.querySelector("[name='" + campo + "']");
      if (!input) return;
      var contenedor = input.closest(".form-field");
      if (!contenedor) return;
      contenedor.classList.add("tiene-error");
      var msg = document.createElement("p");
      msg.className = "error-campo";
      msg.textContent = texto;
      contenedor.appendChild(msg);
    }

    $$("form[data-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();

        var status = form.querySelector(".form-status");
        var submit = form.querySelector("[type=submit]");
        var destino = form.getAttribute("action") || "/api/contacto";

        limpiarErrores(form);
        if (status) { status.textContent = ""; status.classList.remove("error"); }

        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }

        if (submit) {
          submit.disabled = true;
          submit.dataset.label = submit.dataset.label || submit.textContent;
          submit.textContent = "Enviando…";
        }

        var datos = {};
        new FormData(form).forEach(function (valor, clave) { datos[clave] = valor; });

        fetch(destino, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(datos)
        })
          .then(function (r) {
            return r.json().then(function (d) { return { ok: r.ok, datos: d }; });
          })
          .then(function (res) {
            if (res.ok && res.datos.ok) {
              if (status) {
                status.textContent = res.datos.mensaje ||
                  "¡Gracias! Recibimos tu consulta y te vamos a contactar a la brevedad.";
              }
              form.reset();
              if (form === modalForm) window.setTimeout(closeModal, 2000);
              return;
            }
            if (res.datos.errores) {
              Object.keys(res.datos.errores).forEach(function (campo) {
                marcarError(form, campo, res.datos.errores[campo]);
              });
            }
            if (status) {
              status.textContent = res.datos.error || "No pudimos enviar tu consulta.";
              status.classList.add("error");
            }
          })
          .catch(function () {
            if (status) {
              status.textContent =
                "No pudimos enviar tu consulta. Probá de nuevo o escribinos por WhatsApp.";
              status.classList.add("error");
            }
          })
          .then(function () {
            if (submit) {
              submit.disabled = false;
              submit.textContent = submit.dataset.label || "Enviar";
            }
          });
      });
    });

    /* ---------------------------------------------------------------
       Blog: filtro por categoría en el listado
       --------------------------------------------------------------- */
    var filtros = $$(".tag[data-filtro]");
    if (filtros.length) {
      var destacado = $("#destacado");
      var vacio = $("#sin-resultados");
      var tarjetas = $$(".post-card[data-categoria]");

      var aplicar = function (cat) {
        var visibles = 0;
        tarjetas.forEach(function (card) {
          var coincide = cat === "todos" || card.dataset.categoria === cat;
          if (card.closest("#destacado")) {
            if (destacado) destacado.hidden = !coincide;
          } else {
            card.hidden = !coincide;
          }
          if (coincide) visibles++;
        });
        if (vacio) vacio.classList.toggle("is-visible", visibles === 0);
        filtros.forEach(function (b) {
          b.setAttribute("aria-pressed", String(b.dataset.filtro === cat));
        });
      };

      filtros.forEach(function (btn) {
        btn.addEventListener("click", function () { aplicar(btn.dataset.filtro); });
      });

      // Permite entrar directo a una categoría: blog/index.html#cat=Cheques
      var hash = decodeURIComponent(window.location.hash.replace("#cat=", ""));
      if (hash && filtros.some(function (b) { return b.dataset.filtro === hash; })) aplicar(hash);
    }

    /* ---------------------------------------------------------------
       Blog: copiar el link del artículo
       --------------------------------------------------------------- */
    $$("[data-copiar-link]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var aviso = btn.parentElement ? btn.parentElement.querySelector(".copy-ok") : null;
        var mostrar = function () {
          if (!aviso) return;
          aviso.classList.add("is-visible");
          window.setTimeout(function () { aviso.classList.remove("is-visible"); }, 2200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(window.location.href).then(mostrar, function () {});
        } else {
          var tmp = document.createElement("input");
          tmp.value = window.location.href;
          document.body.appendChild(tmp);
          tmp.select();
          try { document.execCommand("copy"); mostrar(); } catch (err) {}
          document.body.removeChild(tmp);
        }
      });
    });

    /* ---------------------------------------------------------------
       Simulador de cuotas (páginas de servicio que lo incluyan).
       La tasa y el link de WhatsApp vienen del HTML, que a su vez sale
       de tools/servicios.py. Acá no hay ningún número hardcodeado.
       --------------------------------------------------------------- */
    var sim = $("#simulador");
    if (sim) {
      var monto = $("#sim-monto", sim);
      var etiquetaMonto = $("#sim-monto-label", sim);
      var salidaCuota = $("#sim-cuota", sim);
      var salidaTotal = $("#sim-total", sim);
      var cta = $("#sim-cta", sim);
      var botones = $$(".plazo-btn", sim);

      var tasa = parseFloat(sim.dataset.tasa) || 0;
      var waBase = sim.dataset.wa || "";
      var activo = botones.filter(function (b) {
        return b.getAttribute("aria-pressed") === "true";
      })[0] || botones[0];
      var plazo = activo ? parseInt(activo.dataset.plazo, 10) : 12;

      var pesos = function (n) {
        return "$ " + Math.round(n).toLocaleString("es-AR");
      };

      function calcular() {
        var capital = parseInt(monto.value, 10);
        // Sistema francés: cuota fija. Con tasa 0 es simplemente capital/plazo.
        var cuota = tasa > 0
          ? capital * tasa / (1 - Math.pow(1 + tasa, -plazo))
          : capital / plazo;
        var total = cuota * plazo;

        etiquetaMonto.textContent = pesos(capital);
        salidaCuota.textContent = pesos(cuota);
        salidaTotal.textContent = pesos(total);

        if (cta && waBase) {
          var texto = "\n\nMonto: " + pesos(capital) + " · Plazo: " + plazo + " meses";
          cta.href = waBase + encodeURIComponent(texto);
        }
      }

      monto.addEventListener("input", calcular);

      botones.forEach(function (btn) {
        btn.addEventListener("click", function () {
          botones.forEach(function (b) {
            b.classList.remove("btn-brand");
            b.classList.add("btn-outline");
            b.setAttribute("aria-pressed", "false");
          });
          btn.classList.remove("btn-outline");
          btn.classList.add("btn-brand");
          btn.setAttribute("aria-pressed", "true");
          plazo = parseInt(btn.dataset.plazo, 10);
          calcular();
        });
      });

      calcular();
    }

    // Estado inicial
    onScroll();
  });
})();
