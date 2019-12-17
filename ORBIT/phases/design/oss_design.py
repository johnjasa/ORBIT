"""Provides the 'OffshoreSubstationDesign` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "Jake.Nunemaker@nrel.gov"


import numpy as np
from ORBIT.phases.design import DesignPhase


class OffshoreSubstationDesign(DesignPhase):
    """Offshore Substation Design Class."""

    expected_config = {
        "site": {"depth": "float"},
        "plant": {"num_turbines": "int"},
        "turbine": {"turbine_rating": "int | float"},
        "substation_design": {
            "mpt_cost_rate": "float (optional)",
            "topside_fab_cost_rate": "float (optional)",
            "topside_design_cost": "float (optional)",
            "shunt_cost_rate": "float (optional)",
            "switchgear_cost": "float (optional)",
            "backup_gen_cost": "float (optional)",
            "workspace_cost": "float (optional)",
            "other_ancillary_cost": "float (optional)",
            "topside_assembly_factor": "float (optional)",
            "substation_jacket_cost_rate": "float (optional)",
            "substation_pile_cost_rate": "float (optional)",
            "num_substations": "int (optional)",
            "design_time": "float (optional)",
        },
    }

    output_config = {
        "num_substations": "int",
        "offshore_substation_topside": "dict",
        "offshore_substation_substructure": "dict",
    }

    def __init__(self, config, **kwargs):
        """
        Creates an instance of OffshoreSubstationDesign.

        Parameters
        ----------
        config : dict
        """

        self.config = self.initialize_library(config, **kwargs)
        self._outputs = {}

    def run(self):
        """Main run function."""

        self.calc_substructure_length()
        self.calc_substructure_deck_space()
        self.calc_topside_deck_space()

        self.calc_num_mpt_and_rating()
        self.calc_mpt_cost()
        self.calc_topside_mass_and_cost()
        self.calc_shunt_reactor_cost()
        self.calc_switchgear_cost()
        self.calc_ancillary_system_cost()
        self.calc_assembly_cost()
        self.calc_substructure_mass_and_cost()
        self.calc_substation_cost()

        self._outputs["offshore_substation_substructure"] = {
            "type": "Monopile",  # Substation install only supports monopiles
            "deck_space": self.substructure_deck_space,
            "weight": self.substructure_mass,
            "length": self.substructure_length,
        }

        self._outputs["offshore_substation_topside"] = {
            "type": "Topside",
            "deck_space": self.topside_deck_space,
            "weight": self.topside_mass,
        }

        self._outputs["num_substations"] = self.num_substations

    def calc_substructure_length(self):
        """
        Calculates substructure length as the site depth + 10m
        """

        self.substructure_length = self.config["site"]["depth"] + 10

    def calc_substructure_deck_space(self):
        """
        Calculates required deck space for the substation substructure.

        Coming soon!
        """

        self.substructure_deck_space = 1

    def calc_topside_deck_space(self):
        """
        Calculates required deck space for the substation topside.

        Coming soon!
        """

        self.topside_deck_space = 1

    def calc_num_mpt_and_rating(self):
        """
        Calculates the number of main power transformers (MPTs) and their rating.

        Parameters
        ----------
        num_turbines : int
        turbine_rating : float
        """

        num_turbines = self.config["plant"]["num_turbines"]
        turbine_rating = self.config["turbine"]["turbine_rating"]

        self.num_mpt = np.ceil(num_turbines * turbine_rating / 250)
        self.mpt_rating = (
            round(
                ((num_turbines * turbine_rating * 1.15) / self.num_mpt) / 10.0
            )
            * 10.0
        )

    def calc_mpt_cost(self):
        """
        Calculates the total cost for all MPTs.

        Parameters
        ----------
        mpt_cost_rate : float
        """

        mpt_cost_rate = self.config["substation_design"].get(
            "mpt_cost_rate", 12500
        )

        self.mpt_cost = self.mpt_rating * self.num_mpt * mpt_cost_rate

    def calc_topside_mass_and_cost(self):
        """
        Calculates the mass and cost of the substation topsides.

        Parameters
        ----------
        topside_fab_cost_rate : int | float
        topside_design_cost: int | float
        """

        topside_fab_cost_rate = self.config["substation_design"].get(
            "topside_fab_cost_rate", 14500
        )
        topside_design_cost = self.config["substation_design"].get(
            "topside_design_cost", 4.5e6
        )

        self.topside_mass = 3.85 * self.mpt_rating * self.num_mpt + 285
        self.topside_cost = (
            self.topside_mass * topside_fab_cost_rate + topside_design_cost
        )

    def calc_shunt_reactor_cost(self):
        """
        Calculates the cost of the shunt reactor.

        Parameters
        ----------
        shunt_cost_rate : int | float
        """
        shunt_cost_rate = self.config["substation_design"].get(
            "shunt_cost_rate", 35000
        )

        self.shunt_reactor_cost = (
            self.mpt_rating * self.num_mpt * shunt_cost_rate * 0.5
        )

    def calc_switchgear_cost(self):
        """
        Calculates the cost of the switchgear.
        # TODO: Is Legacy switchgear cost per MPT or total cost value?

        Parameters
        ----------
        switchgear_cost : int | float
        """

        switchgear_cost = self.config["substation_design"].get(
            "switchgear_cost", 14.5e5
        )
        self.switchgear_costs = self.num_mpt * switchgear_cost

    def calc_ancillary_system_cost(self):
        """
        Calculates cost of ancillary systems.

        Parameters
        ----------
        backup_gen_cost : int | float
        workspace_cost : int | float
        other_ancillary_cost : int | float
        """

        backup_gen_cost = self.config["substation_design"].get(
            "backup_gen_cost", 1e6
        )
        workspace_cost = self.config["substation_design"].get(
            "workspace_cost", 2e6
        )
        other_ancillary_cost = self.config["substation_design"].get(
            "other_ancillary_cost", 3e6
        )

        self.ancillary_system_costs = (
            backup_gen_cost + workspace_cost + other_ancillary_cost
        )

    def calc_assembly_cost(self):
        """
        Calculates the cost of assembly on land.

        Parameters
        ----------
        topside_assembly_factor : int | float
        """

        topside_assembly_factor = self.config["substation_design"].get(
            "topside_assembly_factor", 0.075
        )
        self.land_assembly_cost = (
            self.switchgear_costs
            + self.shunt_reactor_cost
            + self.ancillary_system_costs
        ) * topside_assembly_factor

    def calc_substructure_mass_and_cost(self):
        """
        Calculates the mass and associated cost of the substation substructure.
        Assumes a jacket.

        Parameters
        ----------
        substation_jacket_cost_rate : int | float
        substation_pile_cost_rate : int | float
        """

        substation_jacket_cost_rate = self.config["substation_design"].get(
            "substation_jacket_cost_rate", 6250
        )
        substation_pile_cost_rate = self.config["substation_design"].get(
            "substation_pile_cost_rate", 2250
        )

        substructure_jacket_mass = 0.4 * self.topside_mass
        substructure_pile_mass = 8 * substructure_jacket_mass ** 0.5574
        self.substructure_cost = (
            substructure_jacket_mass * substation_jacket_cost_rate
            + substructure_pile_mass * substation_pile_cost_rate
        )

        self.substructure_mass = (
            substructure_jacket_mass + substructure_pile_mass
        )

    def calc_substation_cost(self):
        """
        Calculates the total cost of the substation solution, based on the
        number of configured substations.

        Parameters
        ----------
        num_substations : int
        """

        self.num_substations = self.config["substation_design"].get(
            "num_substations", 1
        )

        self.substation_cost = (
            sum(
                [
                    self.mpt_cost,
                    self.topside_cost,
                    self.shunt_reactor_cost,
                    self.switchgear_costs,
                    self.ancillary_system_costs,
                    self.land_assembly_cost,
                    self.substructure_cost,
                ]
            )
            * self.num_substations
        )

    @property
    def design_result(self):
        """
        Returns the results of self.run().
        """

        if not self._outputs:
            raise Exception("Has OffshoreSubstationDesign been ran yet?")

        return self._outputs

    @property
    def total_phase_cost(self):
        """Returns total phase cost in $USD."""

        if not self._outputs:
            raise Exception("Has OffshoreSubstationDesign been ran yet?")

        return self.substation_cost

    @property
    def total_phase_time(self):
        """Returns total phase time in hours."""

        phase_time = self.config["substation_design"].get("design_time", 0.0)
        return phase_time

    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        return {}
