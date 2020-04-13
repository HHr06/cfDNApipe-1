# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 14:25:33 2020

@author: Jiaqi Huang
"""

from .StepBase import StepBase
from .cfDNA_utils import commonError, wig2df, correctReadCount
import pandas as pd
import os
from .Configure import Configure

__metaclass__ = type


class GCCorrect(StepBase):
    def __init__(
        self,
        readInput=None,
        gcwigInput=None,
        readtype=None,
        corrkey=None,
        outputdir=None,
        stepNum=None,
        readupstream=None,
        gcupstream=None,
        **kwargs
    ):
        """
        This function is used for processing GC correction on read count data in wig or csv/txt files.

        GCcorrect(readInput=None, gcwigInput=None, outputdir=None, stepNum=None, readupstream=None, gcupstream=None)
        {P}arameters:
            readInput: list, paths of input files of read counts.
            gcwigInput: list, paths of wig files of gc contents.
            readtype: int, file type of readInput, 1 for .wig, 2 for .txt/.csv.; 1 is set by default.
            corrkey: char, type of GC correction, "-" for minus, "/" for divide, "0" for process without GC correction; "/" is set by default
            outputdir: str, output result folder, None means the same folder as input files.
            stepNum: Step number for folder name.
            readupstream: Not used parameter, do not set this parameter.
            gcupstream: Not used parameter, do not set this parameter.
        """

        super(GCCorrect, self).__init__(stepNum, readupstream)

        # set some input
        if ((readupstream is None) and (gcupstream is None)) or (readupstream is True) or (gcupstream is True):
            self.setInput("readInput", readInput)
            self.setInput("gcwigInput", gcwigInput)
            if readtype is not None:
                self.setParam("readtype", readtype)
            else:
                self.setParam("readtype", 1)
            if corrkey is not None:
                self.setParam("corrkey", corrkey)
            else:
                self.setParam("corrkey", "/")
        else:
            Configure.configureCheck()
            readupstream.checkFilePath()
            gcupstream.checkFilePath()
            if readupstream.__class__.__name__ == "runCounter":
                self.setInput("readInput", readupstream.getOutput("wigOutput"))
                self.setParam("readtype", 1)
                if corrkey is not None:
                    self.setParam("corrkey", corrkey)
                else:
                    self.setParam("corrkey", "/")
            elif readupstream.__class__.__name__ == "fpCounter":
                self.setInput("readInput", readupstream.getOutput("txtOutput"))
                self.setParam("readtype", 2)
                if corrkey is not None:
                    self.setParam("corrkey", corrkey)
                else:
                    self.setParam("corrkey", "-")
            else:
                raise commonError("Parameter upstream must from runCounter or fpCounter.")
            if gcupstream.__class__.__name__ == "runCounter":
                self.setInput("gcwigInput", gcupstream.getOutput("wigOutput"))
            else:
                raise commonError("Parameter upstream must from runCounter.")

        self.checkInputFilePath()

        if (readupstream is None) and (gcupstream is None):
            if outputdir is None:
                self.setOutput("outputdir", os.path.dirname(os.path.abspath(self.getInput("readInput")[0])))
            else:
                self.setOutput("outputdir", outputdir)
        else:
            self.checkInputFilePath()
            self.setOutput("outputdir", self.getStepFolderPath())

        self.setOutput(
            "txtOutput",
            [
                os.path.join(self.getOutput("outputdir"), self.getMaxFileNamePrefixV2(x)) + "_gc_cor.txt"
                for x in self.getInput("readInput")
            ],
        )

        self.setOutput(
            "plotOutput",
            [
                os.path.join(self.getOutput("outputdir"), self.getMaxFileNamePrefixV2(x)) + "_gc_cor.png"
                for x in self.getInput("readInput")
            ],
        )

        finishFlag = self.stepInit(readupstream)

        multi_run_len = len(self.getInput("readInput"))

        if not finishFlag:
            gc_df = wig2df(self.getInput("gcwigInput")[0])
            for i in range(multi_run_len):
                print("Now, processing", self.getMaxFileNamePrefixV2(self.getInput("readInput")[i]), "...")
                if self.getParam("readtype") == 1:
                    read_df = wig2df(self.getInput("readInput")[i])
                elif self.getParam("readtype") == 2:
                    read_df = pd.read_csv(self.getInput("readInput")[i], sep="\t", header=0, index_col=None)
                correctReadCount(
                    read_df,
                    gc_df,
                    self.getOutput("txtOutput")[i],
                    self.getOutput("plotOutput")[i],
                    self.getParam("corrkey"),
                )

        self.stepInfoRec(cmds=[], finishFlag=finishFlag)
