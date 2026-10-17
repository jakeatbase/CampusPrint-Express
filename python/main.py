"""CampusPrint Express - PyScript logic.

`document` is Python's view of the web page (like JavaScript's document).
`@when(event, selector)` runs a Python function whenever that event
happens on any element matching the CSS selector.
"""
from pyscript import document, when

# ---- Editable sample prices (Philippine pesos) ----
PRICE_PER_PAGE = {"bw": 2.00, "color": 8.00}       # per page
PAPER_FACTOR = {"A4": 1.0, "Letter": 1.0, "Legal": 1.15}  # Legal costs a bit more
BINDING_FEE = 30.00                                 # per copy
PRINT_LABELS = {"bw": "Black & White", "color": "Color"}


def el(element_id):
    """Shortcut: find an HTML element by its id."""
    return document.getElementById(element_id)


def peso(amount):
    return f"₱{amount:,.2f}"


def to_int(text):
    """Turn text into a whole number, or return None if it isn't one."""
    try:
        return int(text)
    except ValueError:
        return None


def calculate_total(printing, paper, pages, copies, binding):
    """Estimated total = (pages x price x paper factor + binding) x copies."""
    per_copy = pages * PRICE_PER_PAGE[printing] * PAPER_FACTOR[paper]
    if binding == "bound":
        per_copy += BINDING_FEE
    return per_copy * copies


def update_total(event=None):
    """Recalculate the live estimate. Shows 0 while the numbers are invalid."""
    pages, copies = to_int(el("pages").value), to_int(el("copies").value)
    if pages is None or copies is None or pages < 1 or copies < 1:
        el("total").textContent = peso(0)
        return
    total = calculate_total(el("printing").value, el("paper").value, pages, copies, el("binding").value)
    el("total").textContent = peso(total)


def set_error(field_id, error_id, message):
    """Show (or clear) a validation message under a field."""
    el(error_id).textContent = message
    if message:
        el(field_id).classList.add("invalid")
        el(field_id).setAttribute("aria-invalid", "true")
    else:
        el(field_id).classList.remove("invalid")
        el(field_id).removeAttribute("aria-invalid")


def validate():
    """Check every field. Returns True only if the form is valid."""
    ok = True
    checks = [("student-name", "err-name", "Enter your name."),
              ("contact", "err-contact", "Enter an email or phone number."),
              ("doc-name", "err-doc", "Enter the document name.")]
    for field_id, error_id, message in checks:
        empty = el(field_id).value.strip() == ""
        set_error(field_id, error_id, message if empty else "")
        ok = ok and not empty

    pages, copies = to_int(el("pages").value), to_int(el("copies").value)
    if pages is None or pages < 1 or pages > 1000:
        set_error("pages", "err-pages", "Enter 1 to 1000 pages.")
        ok = False
    else:
        set_error("pages", "err-pages", "")
    if copies is None or copies < 1 or copies > 500:
        set_error("copies", "err-copies", "Enter 1 to 500 copies.")
        ok = False
    else:
        set_error("copies", "err-copies", "")
    return ok


def apply_service(service):
    """Set the printing type / binding fields to match the chosen service."""
    el("service").value = service
    if service in ("bw", "color"):
        el("printing").value = service
    elif service == "binding":
        el("binding").value = "bound"
    elif service == "poster":
        el("printing").value = "color"
        el("notes").value = "Poster / large-format project. Please include size and quantity."


def open_order(service="bw"):
    """Open the order form, optionally preselecting a service."""
    el("summary").hidden = True
    el("order-form").hidden = False
    apply_service(service)
    update_total()
    el("order-dialog").showModal()


# ---------------- Event handlers ----------------

@when("click", ".nav-link")
def on_nav_click(event):
    """Scroll to the section named in the link's data-target."""
    event.preventDefault()
    el(event.currentTarget.getAttribute("data-target")).scrollIntoView({"behavior": "smooth"})


@when("click", ".logo")
def on_logo_click(event):
    event.preventDefault()
    el("top").scrollIntoView({"behavior": "smooth"})


@when("click", "#explore-btn")
def on_explore(event):
    el("services").scrollIntoView({"behavior": "smooth"})


@when("click", ".order-btn")
def on_order_button(event):
    open_order()


@when("click", ".arrow")
def on_arrow_click(event):
    """Each card arrow opens the order form with its service selected."""
    open_order(event.currentTarget.getAttribute("data-service"))


@when("change", "#service")
def on_service_change(event):
    apply_service(el("service").value)
    update_total()


@when("click", "#close-dialog")
def on_close(event):
    el("order-dialog").close()


@when("input", "#order-form")
def on_form_change(event):
    update_total()   # runs on every keystroke or selection change


@when("change", "#order-form")
def on_form_select(event):
    update_total()


@when("submit", "#order-form")
def on_submit(event):
    event.preventDefault()   # stop the page from reloading
    if not validate():
        return

    pages, copies = int(el("pages").value), int(el("copies").value)
    printing, paper, binding = el("printing").value, el("paper").value, el("binding").value
    total = calculate_total(printing, paper, pages, copies, binding)
    notes = el("notes").value.strip() or "None"

    rows = [("Service", el("service").options.item(el("service").selectedIndex).text),
            ("Student", el("student-name").value.strip()),
            ("Contact", el("contact").value.strip()),
            ("Document", el("doc-name").value.strip()),
            ("Printing", PRINT_LABELS[printing]),
            ("Paper size", paper),
            ("Pages x copies", f"{pages} x {copies}"),
            ("Binding", "With Binding" if binding == "bound" else "None"),
            ("Instructions", notes),
            ("Estimated total", peso(total))]

    summary = el("summary-list")
    summary.innerHTML = ""
    for label, value in rows:
        dt, dd = document.createElement("dt"), document.createElement("dd")
        dt.textContent, dd.textContent = label, value   # textContent keeps user text safe
        summary.appendChild(dt)
        summary.appendChild(dd)

    el("success-msg").textContent = "Demo order recorded. Here is your summary."
    el("order-form").hidden = True
    el("summary").hidden = False


@when("click", "#new-order")
def on_new_order(event):
    el("order-form").reset()
    el("pages").value, el("copies").value = "10", "1"
    open_order()
