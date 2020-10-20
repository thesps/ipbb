# -*- coding: utf-8 -*-

from rich.table import Table, Column
from os.path import (
    join,
    split,
    exists,
    basename,
    abspath,
    splitext,
    relpath,
    isfile,
    isdir,
)


class DepFormatter(object):
    """docstring for DepFormatter"""
    def __init__(self, parser):
        super().__init__()
        self.parser = parser

    def _drawPackages(self, aPkgs):
        if not aPkgs:
            return ''

        return ' '.join(list(aPkgs))

    def drawPackages(self):
        """
        Draws the list of packages
        """
        return self._drawPackages(self.parser.packages)

    def drawUnresolvedPackages(self):
        """
        Draws the list of unresolved packages
        """
        return self._drawPackages(self.parser.unresolvedPackages)

    def _drawComponents(self, aPkgs):
        if not aPkgs:
            return ''

        lString = ''
        for pkg in sorted(aPkgs):
            lString += '+ %s (%d)\n' % (pkg, len(aPkgs[pkg]))
            lSortCmps = sorted(aPkgs[pkg])
            for cmp in lSortCmps[:-1]:
                lString += u'  ├──' + str(cmp) + '\n'
            lString += u'  └──' + str(lSortCmps[-1]) + '\n'

        return lString[:-1]

    def drawComponents(self):
        """
        Draws the component tree
        """
        return self._drawComponents(self.parser.packages)

    def drawUnresolvedComponents(self):
        """
        Draws the unresolved component tree
        """
        return self._drawComponents(self.parser.unresolvedComponents)


    def drawDeptreeCommandsSummary(self):
        """
        Draws a deptree commands summary table.
        
        """
        # lCommandKinds = ['setup', 'src', 'hlssrc', 'util', 'addrtab', 'iprepo']
        # lDepTable = Texttable()
        # lDepTable.set_cols_align(['c'] * len(lCommandKinds))
        # lDepTable.add_row(lCommandKinds)
        # lDepTable.add_row([len(self.parser.commands[k]) for k in lCommandKinds])
        # return lDepTable.draw()

        lCommandKinds = ('setup', 'src', 'hlssrc', 'util', 'addrtab', 'iprepo')
        lDepTable = Table( *(Column(c, justify='center') for c in lCommandKinds) )
        lDepTable.add_row( *(str(len(self.parser.commands[k])) for k in lCommandKinds) )
        return lDepTable


    def drawUnresolvedSummary(self):
        """
        Draws a summary table of the unresolved files by category
        """
        lParser = self.parser
        if not lParser.unresolved:
            return ''

        lUnresolved = Table()
        lUnresolved.add_row("packages", "components", "paths")
        lUnresolved.add_row(
            str(len(lParser.unresolvedPackages)),
            str(len(lParser.unresolvedComponents)),
            str(len(lParser.unresolvedPaths)),
        )
        return lUnresolved

    def drawUnresolvedFiles(self):
        """
        Draws the table of unresolved files
        """
        lFNF = self.parser.unresolvedFiles
        if not lFNF:
            return ""

        lFNFTable = Table('path expression', 'package', 'component', 'included by')
        # lFNFTable.set_deco(Texttable.HEADER | Texttable.BORDER)

        for pkg in sorted(lFNF):
            lCmps = lFNF[pkg]
            for cmp in sorted(lCmps):
                lPathExps = lCmps[cmp]
                for pathexp in sorted(lPathExps):
                    lFNFTable.add_row(
                        relpath(pathexp, self.parser.rootdir),
                        pkg,
                        cmp,
                        '\n'.join(
                            [(relpath(src, self.parser.rootdir) if src != '__top__' else '(top)') for src in lPathExps[pathexp]]
                        ),
                    )
        return lFNFTable

    def drawParsingErrors(self):
        """
        Draws a text table detailing parsing errors.
        
        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """

        lErrors = self.parser.errors

        lErrTable = Table('dep file', 'line', 'error')

        for lPkg, lCmp, lDepName, lDepPath, lLineNo, lLine, lErr in lErrors:
            
            lErrTable.add_row(
                    relpath(lDepPath, self.parser.rootdir)+':'+str(lLineNo),
                    "'"+lLine+"'",
                    str(lErr)+(': {}'.format(lErr.__cause__) if hasattr(lErr,'__cause__') else ''),
            )

        return lErrTable.draw()

