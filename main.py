import logging
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from payload_to_db import PayloadToDB
from typing import Tuple


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = Flask(__name__)


def query_sixty_day_average(product_id: int) -> Tuple[int, bool]:
    """Connects to the database and queries the average of the chosen product_id

    Args:
        product_id: The product of which the average price is looked for
    Returns:
        sixty_day_average: The average price of the last 60 days
        product_found: Checks whether the product is tracked in the database within the last 60 days
    """
    with sqlite3.connect("payload_database.db") as conn:
        logging.info("Connected to database")
        sixty_day_average_sql = f"""SELECT product, AVG(price) average_price
                                    FROM pricing 
                                    WHERE timestamp >= CURRENT_TIMESTAMP - 60
                                    AND product = {product_id}
                                    GROUP BY product"""
        result = conn.execute(sixty_day_average_sql)
        row = result.fetchone()

        if row is None:
            sixty_day_average = None
            product_found = False
        else:
            sixty_day_average = row[1]
            product_found = True

        return sixty_day_average, product_found


@app.route("/", methods=["POST", "GET"])
def index():
    """Takes the POST-input from the form and redirects to the output page"""
    if request.method == 'POST':
        logger.info("POST-request")
        result = request.form
        product_id = result['product_id']
        return redirect(url_for('get', product_id=product_id))
    return render_template("index.html")


@app.route(f"/<product_id>", methods=["GET"])
def get(product_id: int) -> dict:
    """Returns a dict which concludes the 60-day average price, product id and a check whether the
    requested product id exists"""
    sixty_day_average, product_found = query_sixty_day_average(product_id)
    return {"sixty_day_average_price_euro": sixty_day_average,
            "product_id": product_id,
            "product_found": product_found}


if __name__ == '__main__':
    logger.info("Start")
    PayloadToDB().json_source_to_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    logger.info("App got started")
