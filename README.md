# YGgdrashell

USAGE

    python yggdrashell.py OLDDATAFILE [NEWDATAFILE]

GETTING STARTED

1. Make a directory for tickly updated content

        mkdir tickly

2. Copy sample.yaml into this directory

        cp sample.yaml tickly/

3. Edit it according to your game's content

PERFORMING A FULL TICK UPDATE

Without expenses records:

    python yggdrashell.py OLDDATAFILE NEWDATAFILE

e.g.

    python yggdrashell.py tickly/data005.5 tickly/data006.0

With expenses records:

    python yggdrashell.py OLDDATAFILE NEWDATAFILE -e EXPENSESFILE

e.g.

    python yggdrashell.py tickly/data005.5 tickly/data006.0 -e tickly/expenses005.5

PERFORMING A HALF-TICK UPDATE

Without expenses records:

    python yggdrashell.py -n OLDDATAFILE NEWDATAFILE

e.g.

    python yggdrashell.py -n tickly/data005.5 tickly/data006.0

With expenses records:

    python yggdrashell.py -n OLDDATAFILE NEWDATAFILE -e EXPENSESFILE

e.g.

    python yggdrashell.py -n tickly/data005.5 tickly/data006.0 -e tickly/expenses005.5

ADDITIONAL HELP

    Simply contact Kilojoule Proton via email, Discord, or forum PM.
