# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:11:11 2020

@author: Jiaqi Huang
"""


from .StepBase import StepBase
from .cfDNA_utils import commonError, compressMethy
from .Configure import Configure
import os
import shutil


__metaclass__ = type


class compress_methyl(StepBase):
    def __init__(
        self,
        covInput=None,  # list
        outputdir=None,  # str
        threads=1,
        stepNum=None,
        upstream=None,
        **kwargs
    ):

        super(compress_methyl, self).__init__(stepNum, upstream)

        if upstream is None:
            self.setInput("covInput", covInput)
            self.checkInputFilePath()

            if outputdir is None:
                self.setOutput(
                    "outputdir",
                    os.path.dirname(os.path.abspath(
                        self.getInput("covInput")[0])),
                )
            else:
                self.setOutput("outputdir", outputdir)

            self.setParam("threads", threads)

        else:
            Configure.configureCheck()
            upstream.checkFilePath()

            if upstream.__class__.__name__ == "bismark_methylation_extractor":
                self.setInput("covInput", upstream.getOutput("covOutput"))
            else:
                raise commonError(
                    "Parameter upstream must from bismark_methylation_extractor."
                )

            self.setOutput("outputdir", self.getStepFolderPath())
            self.setParam("threads", Configure.getThreads())

        self.setOutput(
            "tbxOutput",
            [
                os.path.join(
                    self.getOutput("outputdir"), self.getMaxFileNamePrefixV2(x)
                )
                + ".gz"
                for x in self.getInput("covInput")
            ],
        )
        self.setOutput(
            "tbiOutput",
            [
                os.path.join(
                    self.getOutput("outputdir"), self.getMaxFileNamePrefixV2(x)
                )
                + ".gz.tbi"
                for x in self.getInput("covInput")
            ],
        )

        finishFlag = self.stepInit(upstream)

        if not finishFlag:
            multi_run_len = len(self.getInput("covInput"))
            for i in range(multi_run_len):
                compressMethy(InputFile=self.getInput("covInput")[i])
                shutil.move(
                    self.getInput("covInput")[
                        i] + ".gz", self.getOutput("tbxOutput")[i]
                )
                shutil.move(
                    self.getInput("covInput")[i] + ".gz.tbi",
                    self.getOutput("tbiOutput")[i],
                )

        self.stepInfoRec(cmds=[], finishFlag=finishFlag)
