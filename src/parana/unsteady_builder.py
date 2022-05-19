import io

from src.parana.observations import obtain_observations
from src.parana.forecast import forecast


def build(start_date):
    # observations = obtain_observations()
    # data = forecast(observations)

    # Build .u
    with open("demo_ina/condicion_de_borde.u01", "r+b") as f:
        return io.BytesIO(f.read())
