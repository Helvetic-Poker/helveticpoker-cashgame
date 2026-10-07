from pathlib import Path
from html import escape
from urllib.parse import urlparse, quote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public"
BASE = "https://cashgame.helveticpoker.ch"
LOGO = "https://pokerturniere.helveticpoker.ch/assets/helvetic-poker-logo.png?v=7"
TOURNAMENTS = "https://pokerturniere.helveticpoker.ch/"

sources = json.loads((DATA / "cashgames-sources.json").read_text(encoding="utf-8"))
games = json.loads((DATA / "cashgames.json").read_text(encoding="utf-8"))

confirmed = [g for g in games if g.get("status") == "confirmed"]
paused = [g for g in games if g.get("status") == "paused"]

def money(v):
    return "—" if v is None else f"CHF {v:,}".replace(",", "'")

def domain(url):
    return (urlparse(url).hostname or "").removeprefix("www.")

PROVIDER_LOGOS = {
    # Deployment sanity check: keep the generator on the explicit build path.
    # Verified full logo/wordmark assets where available; no favicons for the
    # eight brands explicitly audited here.
    "casino-baden": "https://images.ctfassets.net/7q178rxww3yj/NuEGmB2eIvAiGz2LebWok/3bca270f750e422a0cad1ba78a4fa2d8/casinobaden.svg",
    "casino-bad-ragaz": "https://images.ctfassets.net/7q178rxww3yj/4dzvv6pyv3PbpaCsOHDGAO/22d20334d3b553b0e7d3cd16c4292c28/Card_Casino_Bad_Ragaz.svg",
    "casino-basel": "https://media.jobs.ch/media/cfcf4c22-f90e-4525-a202-85ed807c5e53",
    "casino-bern": "https://media.jobs.ch/images/a9efa51a-1c0e-4e26-94b7-018547a987b9/3379x1734.png",
    "casino-courrendlin": "https://www.casinosbarriere.com/favicon.ico",
    "casino-crans-montana": "https://www.gaming1.com/fr/assetslibrary/asset/getasset?assetId=d155aaf7-dea2-4986-9945-0358d79b9204",
    "casino-davos": "https://www.casinodavos.ch/wp-content/uploads/2025/03/cda-logo-circle-2-150x150.jpg",
    "casino-granges-paccot": "https://www.casinosbarriere.com/favicon.ico",
    "casino-interlaken": "https://www.casino-interlaken.ch/favicon.ico",
    "casino-lugano": "https://www.casinolugano.ch/favicon.ico",
    "casino-luzern": "https://www.lucerne-business.com/company/logo/Grand%20Casino%20Luzern%20AG.png",
    "casino-mendrisio": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAMAAAC3Ycb+AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOVBMVEX///8BAQH+/v77+/vv7+8aGhqQkJBra2t9fX0NDQ0nJyfm5ubKyso7OzvZ2dlSUlKfn5+9vb2urq6iIchDAAAgAElEQVR42uycC3vCtg6Gg+TcL07y/3/ssSXZSSBtaQftWfa9z9ZuFAJY1l1OUQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM4hot2vs79jjX5RGiw/Tx6z/4x/YqzTL8FJAKIemypQIokE/KKO3JkvevwzRPKLFouSDhDzoy85Kg54vz/X/Z+EQHcmq/jU24N3yYRNFdhWn3b2iuFDflsePC1V1dS1934cuyPNQNCQNwW3tvXVTxTRdxTUL1Xtu7Jshdsj4xBfB4G8IcDlaJniT/kRlnia6zHK4vYZfoB6vDG2pbTd+yUKQ2XR+WqZjGFZ56YeyyyQpidEvW/KAJlNN9xaB2GINMqxWSfHnGMrZudc3y/NqNKaGYn6OxUkLO7UjKoa7dgsU++cOJOdYYrhLrt+aLqgPYuoFRbwTeEtFUvd6dYfq6F3rIK4k4ZliUF0ZT0hLXyTyYrL6gbfiTTKeg3SMAkwbbkga/JuAVm/Lg4CeZMLCes6NaodZT30Md0jOoTCOw0RKxWeEZ6FUtYb7JTgZvPTfnH8jZeDl4dX5MLP1Wss21U9Y8v/oTg0H3RNZ5l3VA+EsX8a74Z/Bq/Wqq0nKZlAIn8ZXHGRvEc59ywRLRbmD0XCbOaqLWeHtPvvLRY3Vplq5+g+pM4LofwdLsujcpJfEJTkTzQjzVpVXa7b/iDcpX0qc5KV0GYZteeSigKihnT8PJaIiguzig0d3ubi6YfEvHOXGxs/0wstEKcK14MgrPW79b8kjEj9sPuPlETGe/lmiV+8WSx7dBlNHuXKPyqB6I6mY9Kvy8jbGITUv/R3Wmjiu9BCizCcqsekA3haPUt6c2kFiV998qkfWE/Fz/IPm1y0vf+oIRZFU97+xPcqkK1W1hGtYbKZLDVddP1pihDwJnmUy08VRHavloTpYaQulYpJpUW25Coh3kUPqaIcJct81375r1QvqViTA7nV/c8URFaYHteN92Ncap2yIEjdyLGxJaXjpCC0l6fNHxEXVxaMjpRkg9Wu9wv0vO2Lnd/N2Bx8SKH73ayRWi8bB+aDgqSwgLQPkLdGfGE/DcMwueLqgVb4cpuCjENx9AHPX2WJk1r1xMf8hWVkpetGX899WNXJ6xiXH8JizzrcVbm9YO3BcZHgTzaHWxof514iYz1P165Ch6+dFSTmIN801enZqmXdkEIjkYmbfZcGU9puibN2tba+Vhf+p/fhYYkjKLt7njTeq3qLs2iIvf1tBqltu3phetDE62gIDWP+trGI9S2LFXdxNPspz585DdgFczT4/TBXN8SHq1IFL0/S5KecOYfNXDiv1X+LoVP38kAXN841y21xg1fbdNWaVvMbEhGLnvLKEBTkS6wi6K6eh2C3Ssk4qVANWTUWW/RVojuWohb9qNcRp0Sr1J+7eh2maVir2t4mDlUUF41+0xqpQMwG0fP6JT9zXik2i5LitdIHdmFp+9XHAC6YRw2u1aWbGNtx0MWNJkuFVEmG0kv92cdBixgVsHNDqvCIRC7qRfxtpyH0PYFocjfFfSzeop01PAqPS27Trk6DpRAkBcGQeohx0lfnemZQiOTCZcVDtBfjKtkqIVBI51LCp3PWQ4sl0Cv6kLh4e4HwydGoL41edOhtt/qUyMjDtvRDkQ/zxF+LGSQNdvM7t+pU4qMiBJm70zhBrlCkwbDo9b0FhJdUkDuBzPxNpy6JR3AQccfKfu801Y9ac9s0xIoqxOqvpMCf3IU4fqn5R0VQn+6n8ALVn5lZm/tk54XIovT5smHWzoc0rii+dc5DgoJOA2ZdqBioxdXX1b6VsZpvB3jT/m9XrUqpujSiCFLUzDYtjm4PpmJE+ZyQSrb3uU1wzVR9F2VJSsDPuEu2EiBrWuknJouPJhWAKUPw2JUOxkcxq08PBkkMmDroVW1QN4gXWZJUqSnzsvOxsuBzQHc9DYl7b0vUxeA8WcpKhw5lI4fXheWsb5vN2lqQrYpEB7hHM0gSszbqLlgu0fqJUp4S1UVtlwTI+/g2RsP1pTWEk3ExFdkaQ5+LQy0Mi+dtZ3EKqhOSXEZR9XNSvTLkIFJ9V9nXvbzcUsAhPxxrIrU5cpVSsG7HaqVYU59zUL6kzdqK7xLuPDcfZ27WWSlE6k+al4tD1hWfclzbrSK/JDJ5hymZOPP1wbFz8um5Ar1SsW9iRe3TDRSveNFM3RzpLTnhp2yWtsLzZMSOcrHkMqQPbqrLpHrR8CSfLj7EUsAoHZVrubrNp1sWPzvam6xYJJtNny6pH9ra3rn1YF6mJ6JJ7crSXJ4cN4wRbDpPQm5O5ZE4O+xTNr+VtcRJpNrkYpEa5yKj7+96vGbpypWKS866Sibo6n0Bb1yfqBKJq9FqVZ1PHmrY5KcUoErdcd5sz2A+XaJeyilg1DULcmXSO+hY8jDBMjEdDgpZKi+Kdc3aSVydracuk4tV/0w0QJPPKTPtksFyiQme3IpDyuda0h3IImQt9VJKAfX0Llus1yY/n4LiGIUdevTpGic3J7qSUA4SicVUt2t25OGPdGpHN6eWmro1LQ2nbkeQZ98s1lkxe1hHV1+l3FtOW4+pSKjirHZ9ZAmbTW27EAOkmRPWEnIrAdm1G+z9wWrdumbiHGbu7izD2oaNWYcuWLQdlJyR+ZSQXQ9jGd140ANdZ9nnZD692KlEFUuOcoHNbjZyEiJtkjYeOnUSirtBYoTOuldXbhyGgKg6OOi2awZLuXMrSFrhsQq7NrNzGj/FYiLnATbrdVXRlbfl6L11DMUTmE50g1atNEBbC7tFgaU0OdSNErF4vC3L0tdV4/VYcL3kGa1L64htv50riTszpwG6jfthbsauHBeLZ8slzSuILlloNC6qC7d02mSQaTwVgaTy2WmvKmSdDhvvmgBu8bkDbLf0KP0aMyUN8i7dWo9G6E4kQSadr+dlCCzrXNV+7PROAk06SaL+N98kaEnto7m2J9zasV6dOI3UjpJabx+l06qHZ5sGchq1xSaAjfy67c4EemB+nfRUcJ44uqw8NER1UzUeW9hhX+q4R5nuOhNktPaun4YY6OpQhJ1ciAuo8a/8fZ0D6xCe48TuOf3T4KQymZ6Zhx2jw1niS+ZeIzS1leFKy9w0TbUuUy9vl4furj6fJXs9fP+1GU9vNNMGUVRhi/YuT4BSsYkjTYCmOaDYcmW2e9kUxX7QnfKTRI42MCdtWudkVJTTQLYoX7yLR3pTvS3O9W8FlU8BsAglbO+qCSZqDI65rsP+lK3eO8d5AocPvzcRcZ5FIal02F0GbDCX8kEgtjyFcgCX/koFHaVG+5H4XSj+/1YUPEz7c1G8aoCMdHu7XnHCZUacNXLMhRd6zU1aOCVp+9u0vnCiTzc00eGeihfwotn7mP379tjTJ1eOo647FvfKBTu70iWsdq+LZYv2ugIMFYMvj8Sc98VuZacedA0vyut4XDN6mUDq9uGuhzij+TVzd+wU0Ktu87UbyN31IV6pHR+a4H+1DzkKJE3ZvODKJ626d6jI5s6vEWPdtdRs/PGff7dD1zUnbhVuZfy1yToKpH/BsQYpKzTl+b1z7fr0DTOUo3PaJTSHDJ5PjNZx9mBLDA+J0d358/QqussKPl0Raz7u0s+zGkORJorzAfgPVuHlPkSrziceRO+J8VF82g9fwJo5bzOGWxH4EFzLsTJ6lC7fh+ExqNw95/AB9jdG++KTTb2zGwycz16QjexNh3B2cOmk4uc+5BVOXd6nKk/vZqyDyWcfpBnLT+n0rBgV9zPlPI/H54V/V95y3Pypet/dPU8GWM4uMy6761djevpHH60b69ihKj4YahCtc357W/2IH9iiVwtEq6LTeH57aVWRs3eoP78vtfYbSq82lT/+Brc0xVAUh1uL09keabbWPB0GW5bi09edfDj9aOcGi08+pe/tbPW7NUQV98MvIUt15iq+FIgt1Sjfe+9DTiZ92pmJ7vbfsSn/lUB2In9GIDqetLjHoEXrk+zu371c+dxZv96HxKKJ/3Ar2Rznw1s0zwkkjtiuR+N7oiE3P5jnzC6ez6KMvcnK694eNOQ4E/aFSDSvPikVnnzI/7F3Jdpt6zhUAbTv0v9/7JgAN4CUJdXKtDMJ32vPSWNbskAsBC4uliEbK8A3COTtd1jG/EmnuSoQghAcfwPVHOqvkzWikYYURxpyQyDcHZoz4mW6Q6sdstMaviPKGsTlK1kI3zHr+5rrX9vge+FEINzAGVm2rAZG+PQjHyJ/cbpXttz+jBvtv0RnBfx3oiz5FZq2T71I8YGGcIMZugEJWYF8cSbTeU3Ih+GxYI8EUtwRCKO7CnWOwTJnwk1LwyUfUnyqIfLy1S5/7vZs/uSWQAiH4Ch48gLh3kHLTAIHChgJ5IKGXLnDblfFW5BMFEp4l6KsjwUiw57XZVetIpmtcU8g1OOE7wRCiGof62/511zSkCgauHCP7aDPSa8Qqzn4Djnb/bRAUHkQwxaj/yWHIIsF0q+zWONWq6ixM2hO22t4IBCCsANbLTwQ9xUNkZJSd/Zau7w1PgKJjqoDBQkNwd+rIak+6Is084kP6UcGmjnaI0QcNCLLEssdC+Sr5fZaols4esldH2IIBeTCUmJc+012J4DvcMuryPf7kEHsmJeCIKRK89aHdNyfIfLrWJSbxP74lsojgTAfBqGil+7r63MfoiUVjpzxkX1LiMzEdliq9yryuIbgnipIUdSnKqI0RAgEGDYoz9rTZsN48Q3iAW2vx027VdxS95GGZMJanZfYdfZU2Mt+Fz9t8O0aokKqlRIEqAMvPDFZGLOG2kQ6ojzcrZgRSEzvY453xsuIiy/94xoSWcSOYKZy0M82iStu/cHJ9GENsQwikCgIlwtU5DVYDA8eCATySTrx4S5qFN9gjbWoYYL4+AX9Ol06qRcXfuFJL8Vt7RjB6MwjkSqBmKqIMHHPHQwZJbioEqFP/4p+my0Zs30uEIw7NLjJAxOB7PHD4aOXcGDtNt3L9p5qCMZNwp0ldoqoM/UFYdf/IAtuzwmENnzqQWyfkjq9D7pKdSaQNEfHFEpaICLmJyWKlXMa54c0xKSTLVfjNn3FdjIgDYFCLKUgyqeMuiL5lEAsZZ4M+NfSJjhQJfdIRYRIzgTCRjH+lM7uRSkQcQY0hyChm3U5f6Qh/SaRkqYOKTND0wgOQczD5KYkqhIxhut2eF5D6CO3XqcvLGpZ5+iY/wiumyx7W4vw6kVyMNwhZhkwKloLBYHPNKRrarnaRRD8de6kDpb6NybOsUlkrTTFu2rCRyYLlYJQ4ws4bmKpIrTV7pgsa2mbTkcgWkNcOZ/b/9Y4q2iKMcNHGkLdKPy//XN41mOHP0oF4TBGqogchfKYhtDzShQEXLsZahWxqnrdZBHnuigztTmBgCxFLfFBzMR8n2nIebZ3EHl3DPmFjj1IRE7jzlOypv2YhkChU0aWBcymZSFRERHuXQl7VWbfjq3QGiJ0Md7CJmtQfOZDzhaVYawTMTtRKohjrZfhey3SkU/6EBQOzHuQEB0mKnIz7AVQAoGsQI5qfERI+q0aImrxJonWdjqQITmJo6p8To9WDLWCiCy7Pmj3I9wyWRy3SJOVHgx3TeckCjPFscn6XEO6r2otJU1ToiDZCqKzJM9qCOiqXLUmmDKZ4yMcMd5x6ipAse0NOsoyQJRcvrEpAz3Dt2jItJcSKSkCvq8lDs76Q8jzg05dd5Gn+DJVsLgT9vKppZRhL2QEQhwDmfQucdHB9/mQqh1RzkZS8E2OzThG65Ly5zdoyDh93VtteeNgyEFLfI1q46+hfQgkKWf38LH4viirX8vEwrYXdWsa4TuirLa7KRDDk3dZQ7jdXJ7ysgLBiGQmtQvw2Tmk66doiTNhXUriwWP4ZlIL7qLGmeeirNsKwhwuN1InKk/IRdxUQzBJ6QWH82mUVa228XeYX3/ERaZZnrjz0LxDFXk+l9VWtwXi9vjFKEs1Ae25eshum/1L5dC8VRg+zfbaVBYdKMT9rKV8cPP1HdoFe/exhnh+7fsK4gM+gLRiGHVT29RQIQobNg+AmXNIRmFtoezjKEugsJVDWsbAEIUXQdoxntM+iM81hOnu/0BBIlUVZZwuLuESLwP/VcfDPhzt25FApMFYZjcLbH6oHsJbRKtIqKdDqLR3d1TkAR8CJw7sPd4NmG1Em6xkliOOSxV/t96x/BwIRNwR14zhzzSkPRaI/DSSupfIrRQY0Txy48ATJkudoG8IhBt4QDVRT6MMr8p5W5deBwRFkXfqmb4OZl8G+BMfcigpyrBLFfEj3941AOTX6lqMPtYQii3+TEGCJ5R1A0t7HK2qS3YUQg6XFTQk8L+ZLJKvhj3pQ3Tr3jKHXKpQEBEs25D59afS78Vnoiy4q5/Cm9kWy3tQUj9z4tiH8C+6UDB+KMqSxkFkR7ow4EoE6Ms2ZNY8ixPOalsoPzdZpj4r9LNvV6IGy65doUJXTKOs8zSFGfpRWAaxAw0JTRnM42qN1vwc6oQsplIRdB2LvXzWWGjII82ZSdTrmSgrKc8SL1h+lcUuk/QzR4l3BFKtpccRHPsQcPCc2qOvPs5lxSaLccPCi3Dzi+6QmWbBW+TkAbK60+1l8YRTN9eX6NFqd3DD9D8AjXzuVt6+dzqoVtE5digQW1GetvgEfVtD8AQGpL0IJk91xVwDPuo8ju0K0NQaJ3yzkJDXYQIUHd6JFBSUz83fup4JW0QX+aHJMjdBJWVZbhgex2W1apsntmjMc5UAKGHTnDElEMOXt7xb61Aks3oTBcH3TkdBIdZSoxfeqkctJ9ogHPkQC2EzSZOouU1pyFFLW2gGPRHIK9CScErQjcHmrJU+kvw5JsWOdx0T0B4tO5cRj9GojKTGd2ihFE13VSB9O5da/dbqyGSRy13LGIj2vIaAUG5C9g9LLsWTWAqdgKx2zPbrnqEq1HTqpIMN38KDiXNSdSyU1wRSNfuMdih63LCV9yHkdLHl+Y7nPgT/0IeALNJQDnrtVSX7YH9q/CBhke8KZE64Xm4pCKPmMiqyt83b1dbbXKLHZ0cXGON3zrHBMs9/QMSYbK6so1fvUR1iiz6mnaMbPvyFf6xrfJ+vPbOLn7nr6Cgvq977BwLRff9Ji2eWMUIC3tI2UMDBUN9agtHsQt9WGxeCDJNvOfj/QbQuubNjdENQhosMsfnD6NoDRhwp/Hr+/DL3fcB9Gr3GgErEbedjJHRFUPPOIfqK902WtEi4ZhzCSZiWdvU4kPyxavksapGw/ETdzzG3Cdou3KSjydJdyC8SuFFUjOiIhfyEhWwyLzBHgRzrF4YcZqIs2wLpBlK+7dB750PATRI3AtYdbGfMbhCmAglPWECWcuNHLUw6aS4IBD3Wnh6t3uunVHuYjczwB0x3ODtg2+TibYF4BaTpAIs+dp/tcTYW2vM4U/STRYJpFH8RTAzgbXqiIFcgwNnYrCj+P8cw3uqvgQPqlrdRFkbzA1S0upXXVNPkv+Lws6lnk+qa1/rnrnXgvNR4Ev+rtZchaCGTJdYlqlYOXsHGku6dRkpj3f7cVc/A9IzlvRXFiGB7b33D6YURtTa4jSjn2XnQ6a38yWvwkTjTV4Cfz/Huf/vkihD2+mAeL07MQH8mCicB5zx+cNiL4RR0H/QDxS+J++/6Xb/rd/2u3/W7ftfv+l2/6385qxYGNLojZzwP0g8IwWiiHziUuR/46I+mbqyk73NwqCUMgzzCuG/wc9gBovwB+MwzlX7EaHRbg0LbF1yosRPg6prMdoLhXdH3jQdPojvbOSTm3xeIo3pw40+9RNxITvdg7MNzYgoZg3BStaQvjDQBl97xGRqHN/QTVUPimmSDYmQB+FmtqDINXgbgxREAbWF6aPS00xSrn7SJ3I+FUnB/TyDmdgaT513r0W9V8KwHxbCbZOhWOn3ROeHRPSDcXNrUz7ShwQT765PrEX3SraQPXHcz+YVyQW4nuBuyV3i9YrCjckVKZ1z5Mg7HSwoD8942y9LwQHHLpIU732E8NQHR3tdsZsca9MY+CJn8/RzO6+9ynwzqaxkLv0fdUyibqqsq5nKn/T9OjpGH/po2qwNYDHVv/rEd4iq6aVp/rUCFaGardHbG9LSQpDEYTgI8TnwBM6ulHeWIptejH82vK1PldKYPi7HpaVz1l/mF3w7Y9uaT4o5p/lrl3kz29eY+JkL/FfgvpPLcCCMige2a2RsUpAnqrntz9SVOW2xcXpuLqMnq0s91filDH7DY4EARDQ+gAG/iCQPWT/T2rpro5QjBXxGYbmrbpqcHPIqkp6t2tmUw/ubBxw3Y6Ewk388mbBbA0JqGl643MFE7wr0n+f4bOUKiZ0fbaGF7XrwlnxlAZ/CgbHLR8rivBj0zr4SUYhZZephUAO1qnjFva/8GHWgbfvnB0IuacZi3djJgzYnwWQ4s8DJhC12ynIfx9d6XDqJAF7FAd/ReqTRX6JZ1HLe1qfox4GMIB7eM0mfuZicstZlt/foKG+84c5V/QxxuWzCosrP4cRt0zAuzUFCJF+wuNlDCbmOAl8E9gVd2tIRElZUIPwHz+mVE8LUxwmAT/WQ5rIYwsWtsUwS7dVhcORpJQZdZmFiScLe5IM52BtXUhFGW2zqHQlE52ZsPz5qk169u/HrxegfjEohOC/6JKIucnEO5Uke5jXs9dbIjzeTvX1mGgJgezf7o6OTqMlRdjECmuQjgNHqREYhxSaSD3TT6h2G7hwyAxgLouzV2yvyB1eamSyEp1DK6+c6lHyVnrVszxDPljISn3cYsXIUaGK0qWiv//jImq+N+DhfiEn1QpVHRjLLbIezYcJ7x3Ro088X+xmzgxXEjeUNiyZ1eHoNsxuJ9tG1WWQjHzuDsdhDWxDw/y3FNIeIUY6qxcDGv+XnxwBAbEZM27SgGWhQlIxuypPh/zXQZgUxk0/ud414yP309qc4aEki3RW0s4LCITKlRVRQfDEUEcPECIacaCeS1wRms/p/2zmzJcRuGompAkhft/v+PjYiNpCT3vGVUyT1Vycy43V4IEgRBLJI1YEc6FYj8Yzi+/UEgyfaYLKuC6kDXSiDyQwuufsyHc1jTyhp5re2dVohsvSoEKTUmf50+82lERCAfio2mKc7waYV0Ut76ZapbE0hKgTSVQBpLOFKFUQhkFDWY3qw7dDGoVwiRLLFOMufYpXQSiL66DPyHT64KnRSP4UYeFLOFxkWS1gZONcGT6XGaopo6uGUHi/WkiBXy3nRfUKWjKmv6LhBTYakMcK2y0qtKOuuxQnspECkrsvzIPiRHUo5akkeBpIcX6wFXNxhhSwiYRrrXHpJMeBmCru+TZb9srl9OApks1esxhl8oVsguRZXIGGmUX1cI+bBZfmUhkHTSnCzQ9Zc9JNW61DhMa7KY48IrlRVNCd5b3YRXJpX85LLW/99cIVIvQ6a3VAoQW3W43ENkSqaD7jOF2FFT7SH7q2iXlUXcKsdNvRaIm0k/6bSs5URVIJ9eiiRLDh19V1l6Iu3NupueLbkT5LCpx1R4bcdg/JSCJFPoc7s9JH0bb1nzSOlruuWeV0g65L48L69eIZKXLrbTSyy2XwUijy5FkVMXyHuSSfEY21PP2tMK2Yd0tszXbvp4VE4lEDt0LF6lpnZ2WxOSe62QV1jig5y8TFP46B0E8km1EMZtNq89lXuIFM9Vn8u0tfUecl4hnru+crQWlxWijS0k/4L5txWih8l2XrXK/PtzvanLy+vCnU8qSz0VtzqJyArZrDFm370kvysfBArfsFpZYuC0xRWFRqNOkUMrR+J9eFRljdkUMzuh9XsJ9bek4udsfkq1smRnePVDjra0pAmdzOFkDi/yoKtkGd2Tpmd+a85EWd2mJWIeBrUTrdfg4bxzhxVi6UTDus429U0guR2BrRA7fnFO8yErVaubJrtE1lRnyy0uEaMJxGdxm01OG3Q7GIpEpBhvZHhFZZf0Juyt7ckvWLTW+uZOLooV4jc5at6+t/CVagSoWlndh2+nsvw6qGU/YblAwntr5xBzS5re99Q1FYj9wyQydQcra44Vkvyarbg108YTRrSbvfLEzuZzzOgsEL/yk208NRTRFPzc9bItBKIvr64EL0kechEn0fNGxxCt+qv+B13gbLIpVJaN56on9eiEQoVrd5v8HJemXRtp4Grhm5KaY1sit8d++hzWH64T0j5ku0S40PZZZVmbEG5aLkX5s8aWpgKZ850kt+r+nLY2fwHWDyFVPW8kkJe1Z6PqMlFnqe2LlAUSzdBiWxX7U90qsfLbvnBZ+tZPY2hBYu0L+eqHuO/eX2xxpzmLRN67RLi46BW328bxAfixtiqcWd1a1lWIdLfSRlx+52YS6Z6zrpl0phVL/xnZgvdQWaKvxyKEwdztopYtNUvHtDfvt4xIO/aPMd8vipfuY5dbRSfxafTwArISKKmw8txrVzf11ZCFM9h9iLwli/msWiucZnof4soyPb9b9lcwO+tlfU3CflOjyozh/f96x7MfWTbpMT5s6abtnT0v90DdF2vpBNepLyM6aSM9DQaR76OtbvbDSNc9B470RNkPxKI1l3xaI9GynopyiNNjmbT4effQO74YEPksyXhOU1YWWdcP5qFi71Pp5xjSC61UBK/rYrGVGX/Wii188tx+7LLyPS3L/mvJqbD9Ib//X8cc0IOZM+ExtOzQlf0AqGrAWt28flzP6eS3693Ztlv5+rqPrK3nX3htLrtqmTwGgfwUohdYP1Y4s2nH/fmducY5qs0sc1yMUa6PkUY23whYtW/tuBjHxX17HKr2fmmt8EWK/F/lY7mGx8ctF3HNX3Psz1l2Zn3as8sCGP6Yh3bEA8xPhT4AAAJ7SURBVFrMYp2Htg67SsVLJM3PbdA0fPsztbVz/rGloMl7b+tzX2/T9FhHyc7zmKt2PVbwCGfJMH+ey/47y/47Q3vDfBvLNzzfk1jRCd9U92EZhkPJjSIGSutUcNVJRoteWFAJWekLq5fBWRUWgTpaXqNhv1OV6h1eZoXYP6oFLO2LKD0hYUd0so5g+k7DWRVJQY70C+lz0H3Tjy9Ss7RYYREIV/4RzqQibPFoOkb8GXOECjZuITFf3ihbOKKpGaZo/uj2hlhHRWqfBe/lOhuRyq8P8NXNdXP9gW8kjWsdSnn8mghHpPqL+a7J0aWvmIvimmAq34V94HK0UHMUdV3ViHMxlBxUV1ZGs7egiIclXWKWvnn5bY/yuRPf5kp8QaIvI8U5Erf5svqJa5GX/zWHkoUROOzZrZRLy/hBhMiLDWmAIhVVNuNPCn8LXa6OJkc53HSB0GUyadnE2JTB8RuQ+/jcvVXFEHiw9aF4B1Ou+F+XLAxdozGiPv/tFJEjGMzmLT5mKY7G/VxXIqfqoXtK5FshujrYuZirxWne10qh4KotJCtz36mOJZOqv3souqka5nxIL+6UYkyLQq5FTwcuSjYd3yjU7813kKtSX2TjU/z8EExOOejk4hXi8JFdXjkqNQ8JHdVbOPVj63YFRcWKjuBFaqhelj7y3FxvFkTFVkL/76pUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOC/wz8namgjDbeplgAAAABJRU5ErkJggg==",
    "casino-meyrin": "https://www.pasino.ch/favicon.ico",
    "casino-montreux": "https://www.casinosbarriere.com/favicon.ico",
    "casino-prilly": "https://grandcasinoprilly.com/wp-content/uploads/2026/09/Grand-casino-prilly-logo-scaled.png",
    "casino-st-gallen": "https://bin.staticlocal.ch/localplace-logo/1a/1a30eec70836003858431fdb9f5cf3fc0d7bf832/Swiss_Casino_StGallen_2farbig_yellow_black_cmyk_zentriert.png",
    "casino-winterthur": "https://www.swisscasinos.ch/sites/default/files/2025-10/Swiss_Casino_Casino_Winterthur_1farbig_black_zentriert.png",
    "casino-neuenburg": "https://images.ctfassets.net/7q178rxww3yj/5g2NTlUqOZu98CcAZJh6A5/1119ee692730a5dd7e7043226aaaaf97/Card_Casino_Neuchatel.svg",
    "casino-pfaeffikon": "https://images.ctfassets.net/7q178rxww3yj/69SKrqeaccb23XSuZljdsE/0f61378a52d1784f16fa87af2436d2d9/casinopf%C3%A4ffikon.svg",
    "casino-zuerich": "https://bin.staticlocal.ch/localplace-logo/5b/5bcd21c2110ea2ad0b024769faae663f47811e53/Swiss_Casino_Zuerich_2farbig_yellow_black_cmyk_zentriert.png",
}

INLINE_LOGOS = {
    "casino-locarno": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 180"><rect width="500" height="180" rx="12" fill="#0f1420"/><g fill="none" stroke="#dce5e8" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"><path d="M226 36c31-24 64-8 57 16-7 25-41 18-48 37-7 18 13 30 42 27"/></g><text x="250" y="116" text-anchor="middle" fill="#f0c52b" font-family="Arial,sans-serif" font-size="49" font-weight="700">CASINO</text><text x="250" y="151" text-anchor="middle" fill="#fff" font-family="Arial,sans-serif" font-size="27" font-weight="600" letter-spacing="2">LOCARNO</text></svg>""",
}
def favicon(url):
    host = domain(url)
    return f"https://www.google.com/s2/favicons?domain={host}&sz=128" if host else ""

def provider_logo(provider_id, source_url):
    if provider_id == "casino-locarno":
        return "data:image/svg+xml;charset=utf-8," + quote(INLINE_LOGOS["casino-locarno"])
    return PROVIDER_LOGOS.get(provider_id) or favicon(source_url)

def initials(name):
    words = [w for w in re.findall(r"[A-Za-zÄÖÜäöüÀ-ÿ0-9]+", name) if w.lower() not in {"grand", "casino", "swiss"}]
    return "".join(w[0] for w in words[:2]).upper() or "CG"

def shell(title, description, body, canonical):
    return f"""<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{escape(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}">
<meta property="og:site_name" content="Helvetic Poker">
<style>
*{{box-sizing:border-box}}
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");\nhtml{{font-family:Montserrat,Arial,sans-serif}}body{{font-family:Montserrat,Arial,sans-serif;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}\n:root{{--nav:#0c1b27;--nav2:#143244;--red:#e21b35;--red2:#ff4055;--ink:#13263a;--muted:#6f7c8b;--line:#dfe5ea;--bg:#f3f5f7;--green:#16884b;--max:1180px}}\nbody{{margin:0;background:var(--bg);color:var(--ink);font-family:Montserrat,system-ui,sans-serif}}
a{{color:inherit}}
.top{{height:4px;background:var(--red)}}\nheader{{height:88px;background:linear-gradient(100deg,var(--nav),var(--nav2));color:#fff;position:sticky;top:0;z-index:20;box-shadow:0 2px 8px #00101825}}
.nav{{max-width:1180px;height:100%;margin:auto;padding:0 18px;display:flex;align-items:center;gap:28px}}
.brand{{display:flex;align-items:center;text-decoration:none;min-width:92px}}
.brandLogo{{display:block;width:82px;height:82px;object-fit:contain;background:transparent;border:0;border-radius:0;padding:0}}
.links{{display:flex;gap:29px;margin-left:auto;font-size:15px;font-weight:300;letter-spacing:-.015em;text-transform:uppercase;font-family:Arial,sans-serif}}
.links a{{text-decoration:none;opacity:.94;font-family:Arial,sans-serif}}
.links a.active{{position:relative}}
.links a.active:after{{content:"";position:absolute;left:0;right:0;bottom:-23px;height:3px;background:#ff4055;border-radius:3px}}
.menuBtn{{display:none;margin-left:auto;width:44px;height:44px;border:1px solid #ffffff35;border-radius:9px;background:#ffffff10;color:#fff;font-size:25px;line-height:1;cursor:pointer}}
main{{max-width:1120px;margin:auto;padding:26px 18px 55px}}
.crumb{{font-size:13px;color:#687580;margin-bottom:14px}}
.hero{{color:#fff;background:linear-gradient(90deg,#071722e8,#12384fb0),linear-gradient(135deg,#6c8ea0,#28556c 50%,#102432);position:relative;overflow:hidden;border:0;border-radius:0;padding:40px 30px 35px;box-shadow:none;margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);padding-left:max(30px,calc((100vw - 1100px)/2 + 18px));padding-right:max(30px,calc((100vw - 1100px)/2 + 18px))}}
.hero:first-child{{margin-top:-26px}}
h1{{margin:0;font-size:clamp(38px,6vw,60px);line-height:1;margin:0 0 9px;letter-spacing:-.045em;font-weight:600}}
h2{{font-size:25px;margin:30px 0 12px}}
.lead{{color:rgba(255,255,255,.88);font-size:17px;max-width:850px;margin:14px 0 0}}
.stats{{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap}}
.stat{{padding:9px 12px;border:1px solid #e0e5ea;border-radius:10px;background:#fff}}
.stat strong{{display:block;font-size:19px;color:var(--ink)}}
.stat span{{font-size:11px;color:#6c7884}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}}
.card{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;overflow:hidden;box-shadow:0 3px 12px #10223808}}
.card-top{{display:flex;align-items:center;gap:14px;padding:15px 15px 10px}}
.provider-logo{{width:84px;height:58px;min-width:84px;box-sizing:border-box;display:block;border-radius:10px;object-fit:contain;object-position:center;border:1px solid #e3e8ed;background:#fff;padding:7px}}
.provider-logo-fallback{{display:flex;align-items:center;justify-content:center;background:#f0f2f5;color:#26394a;font-size:13px;font-weight:800}}
.provider-name{{font-size:13px;font-weight:800;line-height:1.2}}
.provider-city{{font-size:11px;color:#71808d;margin-top:3px}}
.card-body{{padding:4px 15px 16px}}
.card h3{{margin:0;font-size:22px;line-height:1.1}}
.stakes{{color:#5f6d79;font-size:13px;margin-top:4px;font-weight:700}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:13px}}
.detail{{border-radius:9px;background:#f7f9fa;padding:9px}}
.detail-label{{font-size:10px;color:#788590;text-transform:uppercase;letter-spacing:.04em}}
.detail-value{{font-size:13px;font-weight:800;margin-top:3px}}
.schedule{{margin-top:9px;padding:10px;border-left:3px solid #e21b35;background:#faf7f8;border-radius:7px;font-size:12px;line-height:1.45}}
.pill{{display:inline-block;border-radius:999px;padding:5px 9px;background:#eaf5ed;font-size:11px;font-weight:800;margin-top:12px}}
a.source{{display:inline-block;margin-top:10px;color:#d21935;font-weight:800;text-decoration:none;font-size:12px}}
.casino-card{{display:flex;align-items:center;gap:13px;padding:15px}}
.casino-card .provider-logo{{width:84px;height:58px;min-width:84px}}
.notice{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;padding:20px;margin-top:14px}}
footer{{max-width:1180px;margin:auto;padding:25px 18px;color:#71808d;font-size:13px}}
@media(max-width:1100px){{.links{{display:none}}.menuBtn{{display:block}}}}
@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:720px){{
header{{height:64px}}.nav{{padding:0 12px;gap:12px}}.menuBtn{{display:block}}.hero{{padding:26px 16px 30px}}
.links.open{{display:flex;position:absolute;top:64px;left:10px;right:10px;margin:0;padding:8px;background:#102b3b;border:1px solid #ffffff18;border-radius:0 0 12px 12px;box-shadow:0 8px 18px #00101830;flex-direction:column;gap:0;z-index:30}}
.links.open a{{padding:14px 12px;font-size:13px;border-bottom:1px solid #ffffff12}}.links.open a:last-child{{border-bottom:0}}.links.open a.active:after{{display:none}}
.brandLogo{{width:58px;height:58px}}main{{padding:20px 10px}}.hero{{padding:24px 20px}}.grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<div class="top"></div><header><div class="nav"><a class="brand" href="https://www.helveticpoker.ch/" target="_blank" rel="noopener"><img class="brandLogo" src="{LOGO}" alt="Helvetic Poker"></a><button class="menuBtn" id="menuBtn" aria-label="Menü öffnen" aria-expanded="false">☰</button><nav class="links" id="mobileNav"><a href="https://www.helveticpoker.ch/blog" target="_blank" rel="noopener">News</a><a href="{TOURNAMENTS}">Pokerturniere</a><a class="active" href="{BASE}/">Cash Games</a><a href="https://www.helveticpoker.ch/pokerclubs-schweiz" target="_blank" rel="noopener">Poker Rooms Schweiz</a><a href="https://www.helveticpoker.ch/anbieter" target="_blank" rel="noopener">Online-Anbieter</a><a href="https://www.helveticpoker.ch/recht-sicherheit" target="_blank" rel="noopener">Recht &amp; Sicherheit</a></nav></div></header>
<main>{body}</main>
<footer>Helvetic Poker · <a href="{TOURNAMENTS}" style="color:inherit">Pokerturniere Schweiz</a> · <a href="{BASE}/" style="color:inherit">Cash Games Schweiz</a> · Offizielle Quellen · tägliche Quellenprüfung.</footer>
<script>const menuBtn=document.getElementById("menuBtn"),mobileNav=document.getElementById("mobileNav");if(menuBtn&&mobileNav){{menuBtn.onclick=()=>{{const open=mobileNav.classList.toggle("open");menuBtn.setAttribute("aria-expanded",open?"true":"false");menuBtn.textContent=open?"×":"☰"}};mobileNav.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>{{mobileNav.classList.remove("open");menuBtn.setAttribute("aria-expanded","false");menuBtn.textContent="☰"}}));}}</script>
</body></html>"""

def logo_img(name, source_url, provider_id=None, cls="provider-logo"):
    return f'<img class="{cls}" src="{escape(provider_logo(provider_id, source_url))}" alt="{escape(name)} Logo" loading="lazy">'

def provider_by_id(provider_id):
    return next((s for s in sources if s["id"] == provider_id), None)

def schedule_html(g):
    schedule = str(g.get("schedule") or "—")
    return f'<div class="schedule"><strong>Spielzeit</strong><br>{escape(schedule)}</div>'

def card(g):
    s = provider_by_id(g.get("provider_id"))
    provider = g.get("provider") or (s["name"] if s else "")
    city = g.get("city") or (s["city"] if s else "")
    canton = g.get("canton") or (s["canton"] if s else "")
    buy = "—"
    if g.get("buy_in_note"):
        buy = g.get("buy_in_note")
    elif g.get("min_buy_in") is not None or g.get("max_buy_in") is not None:
        buy = f"{money(g.get('min_buy_in'))} – {money(g.get('max_buy_in'))}"
    source_url = g.get("source_url") or (s["source_url"] if s else BASE)
    return f"""<article class="card">
<div class="card-top">{logo_img(provider, source_url, s.get("id") if s else g.get("provider_id"))}<div><div class="provider-name">{escape(provider)}</div><div class="provider-city">{escape(city)} · {escape(canton)}</div></div></div>
<div class="card-body">
<h3>{escape(g.get("variant",""))} <span class="stakes">{escape(g.get("stakes",""))}</span></h3>
<div class="detail-grid"><div class="detail"><div class="detail-label">Buy-in</div><div class="detail-value">{escape(buy)}</div></div><div class="detail"><div class="detail-label">Status</div><div class="detail-value">Bestätigt</div></div></div>
{schedule_html(g)}
<a class="source" href="{escape(source_url)}" rel="noopener" target="_blank">Offizielle Quelle →</a>
</div></article>"""

def casino_card(s):
    return f"""<a class="card casino-card" href="{BASE}/anbieter/{escape(s["id"])}/">
{logo_img(s["name"], s["source_url"], s["id"])}
<div><div class="provider-name">{escape(s["name"])}</div><div class="provider-city">{escape(s["city"])} · {escape(s["canton"])}</div></div>
</a>"""

OUT.mkdir(exist_ok=True)
# Keep the Search Console verification file in the published root.
verification_file = ROOT / "google7842e2a0234e258b.html"
if verification_file.exists():
    (OUT / verification_file.name).write_text(verification_file.read_text(encoding="utf-8"), encoding="utf-8")
(OUT / "index.html").write_text(shell(
    "Cash Games Schweiz | Helvetic Poker",
    "Aktuelle Poker-Cash-Games in Schweizer Casinos mit Limits, Buy-ins, Spielzeiten und offiziellen Quellen.",
    f"""<section class="hero"><h1>Cash Games Schweiz</h1>
<p class="lead">Aktuelle Poker-Cash-Games in Schweizer Casinos – getrennt vom Turnierkalender.</p>
<div class="stats"><div class="stat"><strong>{len(confirmed)}</strong><span>bestätigte Angebote</span></div><div class="stat"><strong>{len(paused)}</strong><span>pausierte Angebote</span></div><div class="stat"><strong>{len(sources)}</strong><span>geprüfte Anbieter</span></div></div></section>
<h2>Aktuelle Cash Games</h2>
<div class="grid">{''.join(card(g) for g in confirmed)}</div>
<h2 id="casinos">Schweizer Casinos</h2>
<div class="grid">{''.join(casino_card(s) for s in sources)}</div>""",
    BASE + "/"
), encoding="utf-8")

for s in sources:
    sgames = [g for g in games if g.get("provider_id") == s["id"] and g.get("status") == "confirmed"]
    body = f"""<section class="hero"><div class="card-top" style="padding:0 0 14px">{logo_img(s["name"], s["source_url"], s["id"])}<div><h1 style="font-size:clamp(30px,4vw,46px)">{escape(s["name"])}</h1><p class="lead">{escape(s["city"])} · Kanton {escape(s["canton"])}</p></div></div>
<a class="source" href="{escape(s["source_url"])}" rel="noopener" target="_blank">Offizielle Website →</a></section>"""
    if sgames:
        body += '<h2>Bestätigte Cash Games</h2><div class="grid">' + ''.join(card(g) for g in sgames) + '</div>'
    else:
        body += '<div class="notice"><strong>Aktuell keine bestätigten Cash-Game-Daten.</strong><p>Die offizielle Quelle wird täglich geprüft. Nicht bestätigte Informationen werden bewusst nicht als aktiv dargestellt.</p></div>'
    path = OUT / "anbieter" / s["id"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(shell(f'Cash Games {s["name"]} | Helvetic Poker', f'Cash-Game-Informationen für {s["name"]} in {s["city"]}.', body, f'{BASE}/anbieter/{s["id"]}/'), encoding="utf-8")

print(f"Generated homepage and {len(sources)} provider pages.")
