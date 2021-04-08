
# Modules
import time 

# Specific module elements
from ..depparser import Pathmaker
from ..defaults import kTopEntity
from os.path import abspath, join, split, splitext, dirname

class VivadoHlsProjectGenerator(object):
    """
    docstring for VivadoHlsProjectGenerator
    """

    reqsettings = {'device_name', 'device_package', 'device_speed'}

    # --------------------------------------------------------------
    def __init__(self, aProjInfo, aSolution):
        self.projInfo = aProjInfo
        self.solName = aSolution

    # --------------------------------------------------------------
    def write(self, aOutput, aSettings, aComponentPaths, aCommandList, aRootDir):

        write = aOutput
        pathFinder = Pathmaker(aRootDir)

        if not self.reqsettings.issubset(aSettings.keys()):
            raise RuntimeError(f"Missing required variables: {self.reqsettings.difference(aSettings)}")
        lXilinxPart = f'{aSettings["device_name"]}{aSettings["device_package"]}{aSettings["device_speed"]}'

        # ----------------------------------------------------------
        write = aOutput
        
        lTopEntity = aSettings.get('top_entity', kTopEntity)


        # ----------------------------------------------------------

        write('# Autogenerated project build script')
        write(time.strftime("# %c"))
        write()

        write(
            f'open_project -reset {self.projInfo.name} '
        )

        for setup in (c for c in aCommandList['setup'] if not c.finalize):
            write(f'source {setup.filepath}')

        lHlsSrcs = aCommandList['hlssrc'] 

        for src in lHlsSrcs:


            inc = [pathFinder.getPath(src.package, src.component, 'hlssrc')] + [pathFinder.getPath(src.package, src.component, 'hlstb')] if src.testbench else []
            for p,c in src.includeComponents:
                inc += [pathFinder.getPath(p, c, 'hlssrc')]
            lIncludes = ' '.join(['-I'+i for i in inc])

            opts = []
            if src.testbench:
                opts += ['-tb']

            if lIncludes or src.cflags:
                opts += [f'-cflags {{{" ".join( (f for f in (lIncludes, src.cflags) if f))}}}']

            if src.csimflags:
                opts += [f'-csimflags {{{src.csimflags}}}']

            lCommand = f'add_files {" ".join(opts)} {src.filepath}'
            write(lCommand)


        write(f'open_solution -reset {self.solName}')
        write(f'set_part {{{lXilinxPart}}} -tool vivado')

        write(f'set_top {lTopEntity}')

        for setup in (c for c in aCommandList['setup'] if c.finalize):
            write(f'source {setup.filepath}')

        write('close_project')
    # --------------------------------------------------------------
