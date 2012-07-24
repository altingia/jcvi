"""
uses R for statistics and graphics
"""

import os.path as op
import os
import sys

from string import Template
from optparse import OptionParser

from jcvi.formats.base import must_open
from jcvi.apps.base import ActionDispatcher, sh, debug
debug()


class RTemplate (object):
    """
    Creates a R script and runs it
    """
    def __init__(self, template, parameters):

        self.template = Template(template)
        self.parameters = parameters

    def run(self, clean=True):
        """
        Create a temporary file and run it
        """
        template = self.template
        parameters = self.parameters
        # write to a temporary R script
        fw = must_open("tmp", "w")
        path = fw.name

        fw.write(template.safe_substitute(**parameters))
        fw.close()

        sh("Rscript %s" % path)
        if clean:
            os.remove(path)
            # I have no idea why using ggsave, there is one extra image
            # generated, but here I remove it
            rplotspdf = "Rplots.pdf"
            if op.exists(rplotspdf):
                os.remove(rplotspdf)


def main():

    actions = (
        ('rdotplot', 'dot plot based on lastz rdotplot output'),
            )
    p = ActionDispatcher(actions)
    p.dispatch(globals())


def rdotplot(args):
    """
    %prog rdotplotfile

    Dot plot to visualize relationship between two sequences, by plotting
    .rdotplot file (often generated by LASTZ)
    """
    p = OptionParser(rdotplot.__doc__)
    opts, args = p.parse_args(args)

    if len(args) != 1:
        sys.exit(not p.print_help())

    dotplot_template = """
    dots <- read.table('$rdotplotfile', header=T)
    png('$pngfile')
    plot(dots, type='l')
    dev.off()
    """

    rdotplotfile, = args
    assert rdotplotfile.endswith(".rdotplot")
    pngfile = rdotplotfile.replace(".rdotplot", ".png")

    rtemplate = RTemplate(dotplot_template, locals())
    rtemplate.run()


if __name__ == '__main__':
    main()