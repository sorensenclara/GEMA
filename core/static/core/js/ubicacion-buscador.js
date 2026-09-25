/*
 * Buscador de Ubicación/Dirección para Nuevo/Editar Cliente.
 *
 * Búsqueda EXPLÍCITA únicamente (botón "Buscar" o Enter) -- nunca por cada
 * tecla, tal como exige la política de uso del servidor público de
 * Nominatim que consume `cliente:ubicacion-buscar` del lado del servidor
 * (ver core/services/geocoding.py).
 *
 * El servidor es la única autoridad sobre qué datos geográficos terminan
 * guardados: este script solo maneja `geo_seleccion_token` (una referencia
 * opaca a una sugerencia concreta, cacheada en el servidor) y
 * `geo_tocado`. Nunca escribe localidad/provincia/código postal/país en
 * ningún input -- esos campos no existen en el formulario.
 */
(function () {
    'use strict';

    function init(contenedor) {
        var buscarUrl = contenedor.dataset.buscarUrl;
        var inputDireccion = contenedor.querySelector('input[name="direccion"]');
        var botonBuscar = contenedor.querySelector('.gema-ubicacion-buscar-btn');
        var divResultados = contenedor.querySelector('.gema-ubicacion-resultados');
        var divEstado = contenedor.querySelector('.gema-ubicacion-estado');
        var linkManual = contenedor.querySelector('.gema-ubicacion-manual');
        var inputToken = contenedor.querySelector('input[name="geo_seleccion_token"]');
        var inputTocado = contenedor.querySelector('input[name="geo_tocado"]');

        var textoDeLaSeleccion = null; // valor del input en el momento de seleccionar una sugerencia
        var enModoManual = false;

        function limpiarSeleccion() {
            inputToken.value = '';
            textoDeLaSeleccion = null;
        }

        function ocultarResultados() {
            divResultados.style.display = 'none';
            divResultados.innerHTML = '';
        }

        function mostrarEstadoEncontrado() {
            divEstado.innerHTML = '<span class="text-success">&#10003; Ubicación encontrada</span>';
        }

        function mostrarEstadoManual() {
            divEstado.innerHTML = '<span class="text-muted">Dirección ingresada manualmente</span>';
        }

        function limpiarEstado() {
            divEstado.innerHTML = '';
        }

        function activarModoManual() {
            enModoManual = true;
            limpiarSeleccion();
            inputTocado.value = '1';
            ocultarResultados();
            mostrarEstadoManual();
            inputDireccion.readOnly = false;
            inputDireccion.focus();
        }

        function renderResultados(sugerencias) {
            divResultados.innerHTML = '';

            if (sugerencias.length === 0) {
                var sinResultados = document.createElement('p');
                sinResultados.className = 'text-muted small mb-1';
                sinResultados.textContent = 'No encontramos esta ubicación. Revisá la dirección o ingresala manualmente.';
                divResultados.appendChild(sinResultados);
            } else {
                var titulo = document.createElement('p');
                titulo.className = 'small fw-bold mb-1';
                titulo.textContent = 'Seleccioná la ubicación correcta';
                divResultados.appendChild(titulo);

                sugerencias.forEach(function (sugerencia, indice) {
                    var idRadio = 'gema-ubicacion-opcion-' + indice + '-' + Date.now();
                    var wrapper = document.createElement('div');
                    wrapper.className = 'form-check';

                    var radio = document.createElement('input');
                    radio.type = 'radio';
                    radio.className = 'form-check-input';
                    radio.name = 'gema-ubicacion-radio';
                    radio.id = idRadio;
                    radio.addEventListener('change', function () {
                        enModoManual = false;
                        inputDireccion.value = sugerencia.direccion;
                        inputToken.value = sugerencia.token;
                        inputTocado.value = '1';
                        textoDeLaSeleccion = sugerencia.direccion;
                        ocultarResultados();
                        mostrarEstadoEncontrado();
                    });

                    var label = document.createElement('label');
                    label.className = 'form-check-label small';
                    label.setAttribute('for', idRadio);
                    label.textContent = sugerencia.direccion;

                    wrapper.appendChild(radio);
                    wrapper.appendChild(label);
                    divResultados.appendChild(wrapper);
                });
            }

            var atribucion = document.createElement('p');
            atribucion.className = 'text-muted small mt-1 mb-0';
            atribucion.innerHTML = 'Resultados de &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';
            divResultados.appendChild(atribucion);

            divResultados.style.display = 'block';
        }

        function buscar() {
            var texto = inputDireccion.value.trim();
            if (!texto) {
                return;
            }
            limpiarEstado();
            limpiarSeleccion();
            botonBuscar.disabled = true;

            fetch(buscarUrl + '?q=' + encodeURIComponent(texto), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            })
                .then(function (respuesta) { return respuesta.json(); })
                .then(function (datos) {
                    renderResultados(datos.resultados || []);
                })
                .catch(function () {
                    renderResultados([]);
                })
                .finally(function () {
                    botonBuscar.disabled = false;
                });
        }

        botonBuscar.addEventListener('click', buscar);

        inputDireccion.addEventListener('keydown', function (evento) {
            if (evento.key === 'Enter') {
                evento.preventDefault();
                buscar();
            }
        });

        inputDireccion.addEventListener('input', function () {
            // Si el texto cambia después de una selección válida (o de una
            // carga manual ya confirmada), se invalida de inmediato: hay
            // que volver a buscar y seleccionar, o pasar a modo manual de
            // nuevo, antes de poder guardar con datos georreferenciados.
            if (textoDeLaSeleccion !== null && inputDireccion.value !== textoDeLaSeleccion) {
                limpiarSeleccion();
                limpiarEstado();
            }
            if (enModoManual) {
                enModoManual = false;
            }
        });

        linkManual.addEventListener('click', function (evento) {
            evento.preventDefault();
            activarModoManual();
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.gema-ubicacion-buscador').forEach(init);
    });
})();
