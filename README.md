# Transkribus API Client

![Tests](https://github.com/jnphilipp/transkribus-api/actions/workflows/tests.yml/badge.svg)

Python bindings for the new [Transkribus Developer Platform](https://docs.transkribus.org), the old [Transkribus Metagrapho/Processing API](https://www.transkribus.org/metagrapho/documentation) and the [Transkribus Legacy API](https://help.transkribus.org/transkribus-legacy-api).
This project unites my previous separate projects for the [Metagrapho/Processing APIt](https://github.com/jnphilipp/transkribus_metagrapho_api) and [Legacy API](https://github.com/jnphilipp/transkribus_rest_api).


## Usage

```python
import lxml
import transkribus

from time import sleep

with transkribus.open(USERNAME, PASSWORD) as api:
    process_ids = [
        api.metagrapho.process(IMAGE_PATH, line_detection=49272, htr_id=51170)["processId"],
        api.metagrapho.process(IMAGE_URL, line_detection=49272, htr_id=51170)["processId"],
    ]

    done = set()
    while True:
        for process_id in process_ids:
            if process_id in done:
                continue
            match api.metagrapho.status(process_id)["status"].lower():
                case "finished":
                    with open(f"{process_id}-page.xml", "wb") as f:
                        lxml.etree.tostring(api.metagrapho.page(process_id), pretty_print=True)
                    with open(f"{process_id}-alto.xml", "wb") as f:
                        lxml.etree.tostring(api.metagrapho.alto(process_id), pretty_print=True)
                    done.add(process_id)
                case "failed":
                    print(f"{process_id} FAILED")
                    done.add(process_id)
        if len(done) == len(process_ids):
            break
        sleep(10)
```
